"""
Streamlit Web界面
为Sports Scientist Agent (运动科学家)提供友好的Web界面
基于训练数据的科学分析系统
"""

import os
import sys
import streamlit as st
from datetime import datetime
import json
import locale

# 设置UTF-8编码环境
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

# 设置系统编码
try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'C.UTF-8')
    except locale.Error:
        pass

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from InsightEngine import DeepSearchAgent, Config
from config import (
    INSIGHT_ENGINE_API_KEY,
    INSIGHT_ENGINE_BASE_URL,
    INSIGHT_ENGINE_MODEL_NAME,
    DB_HOST,
    DB_USER,
    DB_PASSWORD,
    DB_NAME,
    DB_PORT,
    DB_CHARSET,
)


def main():
    """主函数"""
    st.set_page_config(
        page_title="运动科学家",
        page_icon="🔬",
        layout="wide"
    )

    # 自定义样式
    st.markdown("""
    <style>
        /* 隐藏Streamlit默认页眉和工具栏 */
        header[data-testid="stHeader"] {
            background-color: transparent;
            background: transparent;
        }

        /* 隐藏右上角的部署按钮等 */
        .stDeployButton {
            display: none;
        }

        /* 隐藏顶部工具栏 */
        #MainMenu {
            visibility: hidden;
        }

        footer {
            visibility: hidden;
        }

        /* 主题配色 */
        :root {
            --primary-color: #10b981;
            --secondary-color: #06b6d4;
            --bg-dark: #0f172a;
            --bg-panel: #1e293b;
        }

        /* 标题样式 */
        .main-title {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #10b981 0%, #06b6d4 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
            text-align: center;
        }

        .subtitle {
            font-size: 1.1rem;
            color: #94a3b8;
            text-align: center;
            margin-bottom: 2rem;
        }

        /* 卡片样式 */
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        }

        /* 进度条样式 */
        .stProgress > div > div > div {
            background: linear-gradient(90deg, #10b981 0%, #06b6d4 100%);
        }

        /* 按钮样式 */
        .stButton > button {
            background: linear-gradient(135deg, #10b981 0%, #06b6d4 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
        }

        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
        }

        /* 文本框样式 */
        .stTextArea textarea {
            border-radius: 8px;
            border: 2px solid #334155;
            background: #1e293b;
            color: #e2e8f0;
            font-size: 0.95rem;
        }

        /* 标签页样式 */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background: #1e293b;
            border-radius: 8px;
            padding: 0.5rem;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 6px;
            padding: 0.5rem 1rem;
            background: transparent;
            color: #94a3b8;
        }

        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #10b981 0%, #06b6d4 100%);
            color: white;
        }

        /* Expander样式 */
        .streamlit-expanderHeader {
            background: #1e293b;
            border-radius: 8px;
            border: 1px solid #334155;
        }

        /* 成功/错误/警告消息样式 */
        .stSuccess, .stError, .stWarning {
            border-radius: 8px;
            padding: 1rem;
        }

        /* 增强所有markdown文字颜色 - 确保清晰可读 */
        .stMarkdown, .stMarkdown p, .stMarkdown div, .stMarkdown span {
            color: #e5e7eb !important;  /* 明亮的浅灰色 */
        }

        /* 增强markdown加粗文字 */
        .stMarkdown strong, .stMarkdown b {
            color: #f3f4f6 !important;  /* 更亮的白灰色 */
            font-weight: 700;
        }

        /* 增强所有文本元素 */
        p, div, span, label {
            color: #d1d5db !important;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 class="main-title">Sports Scientist</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">运动科学家 | 生理数据量化分析 | 循证训练建议</p>', unsafe_allow_html=True)

    # 检查URL参数
    try:
        # 尝试使用新版本的query_params
        query_params = st.query_params
        auto_query = query_params.get('query', '')
        auto_search = query_params.get('auto_search', 'false').lower() == 'true'
    except AttributeError:
        # 兼容旧版本
        query_params = st.experimental_get_query_params()
        auto_query = query_params.get('query', [''])[0]
        auto_search = query_params.get('auto_search', ['false'])[0].lower() == 'true'

    # ----- 配置被硬编码 -----
    # 强制使用 Kimi
    model_name = INSIGHT_ENGINE_MODEL_NAME or "kimi-k2-0711-preview"
    # 默认高级配置
    max_reflections = 2
    max_content_length = 500000  # Kimi支持长文本

    # 简化的研究查询展示区域
    
    # 如果有自动查询，使用它作为默认值，否则显示占位符
    display_query = auto_query if auto_query else "等待接收训练数据分析查询...\n\n示例查询:\n- 检测最近一周的平均心率比基准值高出多少\n- 量化分析我的配速稳定性和训练密度\n- 基于生理数据评估最近的训练负荷"
    
    # 只读的查询展示区域
    st.text_area(
        "当前查询",
        value=display_query,
        height=100,
        disabled=True,
        help="查询内容由主页面的搜索框控制",
        label_visibility="hidden"
    )

    # 自动搜索逻辑
    start_research = False
    query = auto_query
    
    if auto_search and auto_query and 'auto_search_executed' not in st.session_state:
        st.session_state.auto_search_executed = True
        start_research = True
    elif auto_query and not auto_search:
        st.warning("等待搜索启动信号...")

    # 验证配置
    if start_research:
        if not query.strip():
            st.error("请输入研究查询")
            return

        # 检查配置中的LLM密钥
        if not INSIGHT_ENGINE_API_KEY:
            st.error("请在您的配置文件(config.py)中设置INSIGHT_ENGINE_API_KEY")
            return

        # 自动使用配置文件中的API密钥和数据库配置
        db_host = DB_HOST
        db_user = DB_USER
        db_password = DB_PASSWORD
        db_name = DB_NAME
        db_port = DB_PORT
        db_charset = DB_CHARSET

        # 创建配置
        config = Config(
            llm_api_key=INSIGHT_ENGINE_API_KEY,
            llm_base_url=INSIGHT_ENGINE_BASE_URL,
            llm_model_name=model_name,
            db_host=db_host,
            db_user=db_user,
            db_password=db_password,
            db_name=db_name,
            db_port=db_port,
            db_charset=db_charset,
            max_reflections=max_reflections,
            max_content_length=max_content_length,
            output_dir="insight_engine_streamlit_reports"
        )

        # 执行研究
        execute_research(query, config)


def execute_research(query: str, config: Config):
    """执行训练数据科学分析"""
    try:
        # 创建进度条
        progress_bar = st.progress(0)
        status_text = st.empty()

        # 初始化Sports Scientist Agent
        status_text.markdown("**正在初始化运动科学分析引擎...**")
        agent = DeepSearchAgent(config)  # DeepSearchAgent是向后兼容的别名,实际为SportsScientistAgent
        st.session_state.agent = agent

        progress_bar.progress(10)

        # 生成报告结构
        status_text.markdown("**正在构建科学分析框架...**")
        agent._generate_report_structure(query)
        progress_bar.progress(20)

        # 处理数据分析模块
        total_paragraphs = len(agent.state.paragraphs)
        for i in range(total_paragraphs):
            status_text.markdown(f"**量化分析 {i + 1}/{total_paragraphs}:** {agent.state.paragraphs[i].title}")

            # 数据查询和量化分析
            agent._initial_search_and_summary(i)
            progress_value = 20 + (i + 0.5) / total_paragraphs * 60
            progress_bar.progress(int(progress_value))

            # 数据验证循环
            agent._reflection_loop(i)
            agent.state.paragraphs[i].research.mark_completed()

            progress_value = 20 + (i + 1) / total_paragraphs * 60
            progress_bar.progress(int(progress_value))

        # 生成科学分析报告
        status_text.markdown("**正在生成科学分析报告...**")
        final_report = agent._generate_final_report()
        progress_bar.progress(90)

        # 保存报告
        status_text.markdown("**正在保存分析结果...**")
        agent._save_report(final_report)
        progress_bar.progress(100)

        status_text.markdown("**生理数据分析完成!**")

        # 显示结果
        display_results(agent, final_report)

    except Exception as e:
        st.error(f"生理数据分析过程中发生错误: {str(e)}")


def display_results(agent: DeepSearchAgent, final_report: str):
    """显示科学分析结果"""
    st.markdown("---")
    st.markdown("## 科学分析报告")

    # 结果标签页
    tab1, tab2 = st.tabs(["分析报告", "数据来源"])

    with tab1:
        st.markdown(final_report)

    with tab2:
        # 数据模块详情
        st.subheader("数据分析模块详情")
        for i, paragraph in enumerate(agent.state.paragraphs):
            with st.expander(f"模块 {i + 1}: {paragraph.title}"):
                st.write("**分析目标:**", paragraph.content)
                st.write("**科学分析结果:**", paragraph.research.latest_summary[:300] + "..."
                if len(paragraph.research.latest_summary) > 300
                else paragraph.research.latest_summary)
                st.write("**数据查询次数:**", paragraph.research.get_search_count())
                st.write("**验证迭代次数:**", paragraph.research.reflection_iteration)

        # 数据查询历史
        st.subheader("训练数据查询历史")
        all_searches = []
        for paragraph in agent.state.paragraphs:
            all_searches.extend(paragraph.research.search_history)

        if all_searches:
            for i, search in enumerate(all_searches):
                with st.expander(f"查询 {i + 1}: {search.query}"):
                    st.write("**数据源:**", search.platform or "训练记录数据库")
                    st.write("**标题:**", search.title)
                    st.write("**数据预览:**",
                             search.content[:200] + "..." if len(search.content) > 200 else search.content)
                    if search.score:
                        st.write("**量化指标:**", search.score)


if __name__ == "__main__":
    main()
