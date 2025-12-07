<div align="center">

<img src="static/image/logo.png" alt="Synapse Run Logo" width="100%">

# Synapse Run

**智能跑步训练助手 | 多智能体协作系统**

[English](./README-EN.md) | [中文文档](./README.md)

</div>

## ⚡ 项目简介

**Synapse Run** 是一个基于多智能体协作架构的中长跑训练助手系统。系统通过"论坛"交互机制,让多个专业AI Agent像神经突触(Synapse)一样相互协作、思维碰撞,为跑者制定科学的训练计划。

> **Synapse寓意**: 多智能体的协作就像大脑中神经突触的连接方式,通过信息传递与相互影响,产生超越单一智能体的集体智慧。

### 核心特性

1. **多智能体"论坛"协作**: 四个专业Agent通过论坛机制进行思维碰撞与辩论,避免单一模型的局限性
2. **数据驱动的训练分析**: 深度挖掘训练数据库,结合互联网专业资源,生成科学的训练建议
3. **智能报告生成**: 动态选择报告模板,多轮优化生成专业的训练分析报告
4. **纯Python模块化设计**: 轻量级架构,易于扩展和定制

**核心技术栈**: Python 3.9+, Flask, Streamlit, OpenAI-compatible LLM APIs, MySQL

---

## 🏗️ 系统架构

### 多智能体协作架构

系统由四个核心Agent组成,每个Agent拥有独立的工具集、提示词模板和处理节点:

1. **Query Agent** (`QueryEngine/`): 专业知识搜索
   - 工具: Tavily API (新闻搜索、网页搜索等)
   - 核心能力: 互联网跑步训练资源检索、专业文献查找

2. **后勤与情报官** (`MediaEngine/`): 跑步训练情报收集专家
   - 工具: 博查网页搜索、结构化数据卡片(天气、价格、百科等)
   - 核心能力: 比赛报名、天气预报、装备价格、路线坡度等实用情报收集

3. **Insight Agent** (`InsightEngine/`): 训练数据深度挖掘
   - 工具: 训练数据库查询工具
   - 核心能力: 历史训练数据分析、统计建模

4. **Report Agent** (`ReportEngine/`): 智能报告生成
   - 工具: 模板选择引擎、报告生成器
   - 核心能力: 训练报告模板动态选择、多轮报告优化

### ForumEngine 论坛协作机制

**核心创新**: Agent间通过"论坛"机制进行思维碰撞与辩论

- **监控模块** (`ForumEngine/monitor.py`): 实时监控Agent日志,提取关键发言
- **主持人模块** (`ForumEngine/llm_host.py`): LLM主持人生成总结和引导
- **论坛日志** (`logs/forum.log`): 所有Agent通过此文件交流
- **工具接口** (`utils/forum_reader.py`): Agent读取论坛内容的统一接口

### 工作流程

| 步骤 | 阶段名称 | 主要操作 | 参与组件 | 循环特性 |
|------|----------|----------|----------|----------|
| 1 | 用户提问 | Flask主应用接收训练问题 | Flask主应用 | - |
| 2 | 并行启动 | 三个Agent同时开始工作 | Query Agent、后勤与情报官、Insight Agent | - |
| 3 | 初步分析 | 各Agent使用专属工具进行概览搜索 | 各Agent + 专属工具集 | - |
| 4 | 策略制定 | 基于初步结果制定分块研究策略 | 各Agent内部决策模块 | - |
| 5-N | **循环阶段** | **论坛协作 + 深度研究** | **ForumEngine + 所有Agent** | **多轮循环** |
| 5.1 | 深度研究 | 各Agent基于论坛主持人引导进行专项搜索 | 各Agent + 反思机制 + 论坛引导 | 每轮循环 |
| 5.2 | 论坛协作 | ForumEngine监控Agent发言并生成主持人总结 | ForumEngine + LLM主持人 | 每轮循环 |
| 5.3 | 交流融合 | 各Agent根据讨论调整研究方向 | 各Agent + forum_reader工具 | 每轮循环 |
| N+1 | 结果整合 | Report Agent收集所有分析结果和论坛内容 | Report Agent | - |
| N+2 | 报告生成 | 动态选择模板和样式,多轮生成最终报告 | Report Agent + 模板引擎 | - |

### 统一Agent架构模式

所有Agent遵循相同的模块化架构:

```
<Agent>/
├── agent.py              # Agent主类,实现完整workflow
├── llms/base.py          # 统一的OpenAI兼容LLM客户端
├── nodes/                # 处理节点
│   ├── base_node.py      # 基础节点类
│   ├── search_node.py    # 搜索节点
│   ├── summary_node.py   # 总结节点
│   └── formatting_node.py # 格式化节点
├── tools/                # 专属工具集
├── state/state.py        # Agent状态管理
├── prompts/prompts.py    # 提示词模板
└── utils/config.py       # 配置管理
```

---

## 🚀 快速开始

### 环境要求

- **操作系统**: Windows、Linux、MacOS
- **Python版本**: 3.9+
- **Conda**: Anaconda或Miniconda
- **数据库**: MySQL
- **内存**: 建议2GB以上

### 1. 创建Conda环境

```bash
# 创建conda环境
conda create -n synapse_run python=3.11
conda activate synapse_run
```

### 2. 安装依赖包

```bash
# 基础依赖安装
pip install -r requirements.txt

# Playwright浏览器驱动(如需使用爬虫功能)
playwright install chromium
```

### 3. 配置系统

#### 3.1 配置API密钥

编辑 `config.py` 文件,填入您的API密钥:

```python
# MySQL数据库配置
DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "your_username"
DB_PASSWORD = "your_password"
DB_NAME = "your_db_name"
DB_CHARSET = "utf8mb4"

# LLM配置
# 您可以更改每个部分LLM使用的API,只要兼容OpenAI请求格式都可以

# Insight Agent
INSIGHT_ENGINE_API_KEY = "your_api_key"
INSIGHT_ENGINE_BASE_URL = "https://api.moonshot.cn/v1"
INSIGHT_ENGINE_MODEL_NAME = "kimi-k2-0711-preview"

# 后勤与情报官
MEDIA_ENGINE_API_KEY = "your_api_key"
MEDIA_ENGINE_BASE_URL = "https://api.example.com/v1"
MEDIA_ENGINE_MODEL_NAME = "your_model_name"

# Query Agent
QUERY_ENGINE_API_KEY = "your_api_key"
QUERY_ENGINE_BASE_URL = "https://api.example.com/v1"
QUERY_ENGINE_MODEL_NAME = "your_model_name"

# Report Agent
REPORT_ENGINE_API_KEY = "your_api_key"
REPORT_ENGINE_BASE_URL = "https://api.example.com/v1"
REPORT_ENGINE_MODEL_NAME = "your_model_name"

# Forum Host
FORUM_HOST_API_KEY = "your_api_key"
FORUM_HOST_BASE_URL = "https://api.siliconflow.cn/v1"
FORUM_HOST_MODEL_NAME = "Qwen/Qwen3-235B-A22B-Instruct-2507"

# 网络工具
TAVILY_API_KEY = "your_tavily_api_key"
BOCHA_WEB_SEARCH_API_KEY = "your_bocha_api_key"
```

**重要**: 所有LLM必须兼容OpenAI请求格式 (api_key + base_url + model_name)

#### 3.2 数据库初始化

初始化MySQL数据库:

```bash
# 使用提供的SQL脚本初始化数据库
mysql -u your_username -p your_db_name < schema/init_database.sql
```

### 4. 启动系统

#### 4.1 完整系统启动(推荐)

```bash
# 在项目根目录下,激活conda环境
conda activate synapse_run

# 启动主应用
python app.py
```

访问 http://localhost:5000 即可使用完整系统

#### 4.2 单独启动某个Agent(调试用)

```bash
# 启动QueryEngine
streamlit run SingleEngineApp/query_engine_streamlit_app.py --server.port 8503

# 启动MediaEngine
streamlit run SingleEngineApp/media_engine_streamlit_app.py --server.port 8502

# 启动InsightEngine
streamlit run SingleEngineApp/insight_engine_streamlit_app.py --server.port 8501
```

---

## ⚙️ 高级配置

### 接入不同的LLM模型

支持任意OpenAI调用格式的LLM提供商,只需要在`config.py`中填写对应的KEY、BASE_URL、MODEL_NAME即可。

OpenAI调用格式示例:
```python
from openai import OpenAI

client = OpenAI(
    api_key="your_api_key",
    base_url="https://api.siliconflow.cn/v1"
)

response = client.chat.completions.create(
    model="Qwen/Qwen2.5-72B-Instruct",
    messages=[
        {'role': 'user', 'content': "我的5公里最好成绩是22分钟,如何提升到20分钟?"}
    ],
)

print(response.choices[0].message.content)
```

### 自定义报告模板

#### 1. 在Web界面中上传

系统支持上传自定义模板文件(.md或.txt格式),可在生成报告时选择使用。

#### 2. 创建模板文件

在 `ReportEngine/report_template/` 目录下创建新的模板,Agent会自动检测并在合适场景选用。

### 修改关键参数

每个Agent都有专门的配置文件,可根据需求调整:

```python
# QueryEngine/utils/config.py
class Config:
    max_reflections = 2           # 反思轮次
    max_search_results = 15       # 最大搜索结果数
    max_content_length = 8000     # 最大内容长度

# MediaEngine/utils/config.py
class Config:
    comprehensive_search_limit = 10  # 综合搜索限制
    web_search_limit = 15           # 网页搜索限制

# InsightEngine/utils/config.py
class Config:
    default_search_topic_globally_limit = 200    # 全局搜索限制
    default_get_comments_limit = 500             # 评论获取限制
    max_search_results_for_llm = 50              # 传给LLM的最大结果数
```

---

## 📂 项目结构

```
Synapse_Run/
├── QueryEngine/                   # 专业知识搜索Agent
│   ├── agent.py                   # Agent主逻辑
│   ├── llms/                      # LLM接口封装
│   ├── nodes/                     # 处理节点
│   ├── tools/                     # 搜索工具
│   └── utils/                     # 工具函数
├── MediaEngine/                   # 后勤与情报官Agent(情报收集)
│   ├── agent.py                   # Agent主逻辑
│   ├── nodes/                     # 处理节点
│   ├── llms/                      # LLM接口
│   ├── tools/                     # 分析工具
│   └── utils/                     # 工具函数
├── InsightEngine/                 # 训练数据深度挖掘Agent
│   ├── agent.py                   # Agent主逻辑
│   ├── llms/                      # LLM接口封装
│   ├── nodes/                     # 处理节点
│   ├── tools/                     # 数据库查询工具
│   ├── state/                     # 状态管理
│   ├── prompts/                   # 提示词模板
│   └── utils/                     # 工具函数
├── ReportEngine/                  # 智能报告生成Agent
│   ├── agent.py                   # Agent主逻辑
│   ├── llms/                      # LLM接口
│   ├── nodes/                     # 报告生成节点
│   ├── report_template/           # 报告模板库
│   └── flask_interface.py         # Flask API接口
├── ForumEngine/                   # 论坛引擎
│   ├── monitor.py                 # 日志监控和论坛管理
│   └── llm_host.py                # 论坛主持人LLM模块
├── SingleEngineApp/               # 单独Agent的Streamlit应用
│   ├── query_engine_streamlit_app.py
│   ├── media_engine_streamlit_app.py
│   └── insight_engine_streamlit_app.py
├── templates/                     # Flask模板
│   └── index.html                 # 主界面前端
├── static/                        # 静态资源
│   └── image/                     # 图片资源
├── logs/                          # 运行日志目录
│   └── forum.log                  # 论坛交流日志
├── reports/                       # 生成的报告文件
├── utils/                         # 通用工具函数
│   ├── forum_reader.py            # Agent间论坛通信
│   └── retry_helper.py            # 网络请求重试机制
├── app.py                         # Flask主应用入口
├── config.py                      # 全局配置文件
├── CLAUDE.md                      # 开发指南
└── requirements.txt               # Python依赖包清单
```

---

## 🤝 贡献指南

我们欢迎所有形式的贡献!

### 如何贡献

1. **Fork项目**到您的GitHub账号
2. **创建Feature分支**: `git checkout -b feature/AmazingFeature`
3. **提交更改**: `git commit -m 'Add some AmazingFeature'`
4. **推送到分支**: `git push origin feature/AmazingFeature`
5. **开启Pull Request**

### 开发规范

- 代码遵循PEP8规范
- 提交信息使用清晰的中英文描述
- 新功能需要包含相应的测试用例
- 更新相关文档

---

## 📄 许可证

本项目采用 [GPL-2.0许可证](LICENSE)。详细信息请参阅LICENSE文件。

---

## 🎉 支持与联系

### 获取帮助

- **项目主页**: [GitHub仓库](https://github.com/your-repo/synapse-run)
- **问题反馈**: [Issues页面](https://github.com/your-repo/synapse-run/issues)
- **功能建议**: [Discussions页面](https://github.com/your-repo/synapse-run/discussions)

---

## ⚠️ 免责声明

**重要提醒: 本项目仅供学习、学术研究和教育目的使用**

1. **合规性声明**:
   - 本项目中的所有代码、工具和功能均仅供学习、学术研究和教育目的使用
   - 严禁将本项目用于任何商业用途或盈利性活动
   - 严禁将本项目用于任何违法、违规或侵犯他人权益的行为

2. **数据使用免责**:
   - 项目涉及的数据分析功能仅供学术研究使用
   - 使用者应确保所分析数据的合法性和合规性

3. **技术免责**:
   - 本项目按"现状"提供,不提供任何明示或暗示的保证
   - 作者不对使用本项目造成的任何直接或间接损失承担责任
   - 使用者应自行评估项目的适用性和风险

4. **责任限制**:
   - 使用者在使用本项目前应充分了解相关法律法规
   - 使用者应确保其使用行为符合当地法律法规要求
   - 因违反法律法规使用本项目而产生的任何后果由使用者自行承担

**请在使用本项目前仔细阅读并理解上述免责声明。使用本项目即表示您已同意并接受上述所有条款。**

---

<div align="center">

**让AI成为你的智能跑步教练 🏃‍♂️**

Made with ❤️ by Synapse Run Team

</div>
