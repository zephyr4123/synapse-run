<div align="center">

<img src="static/image/logo.png" alt="Synapse Run Logo" width="100%">

# Synapse Run

**智能跑步训练助手 | 多智能体协作系统**

[![License: GPL v2](https://img.shields.io/badge/License-GPL%20v2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html) [![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

[English](./README-EN.md) | [中文文档](./README.md)

</div>

---

## 📢 更新日志

### 2025.12.10 - 训练数据导入系统重构与多数据源整合

#### 🔄 核心架构升级
- **统一导入模块**: 合并`import_training_data.py`和`import_garmin_data.py`为统一模块`training_data_importer.py`
- **API专用设计**: 移除所有CLI命令行功能,专注于后端API调用接口,提升系统架构的纯净性
- **基类架构**: 新增`BaseImporter`基类,统一数据库引擎初始化逻辑,便于扩展更多数据源

#### 📦 导入器重构
- **Keep导入器** (`KeepDataImporter`): Excel文件导入,支持.xlsx/.xls/.csv格式,批量提交优化(100条/批次)
- **Garmin导入器** (`GarminDataImporter`): Garmin Connect在线数据抓取,自动登录+活动过滤+批量导入
- **懒加载引擎**: 数据库引擎采用懒加载模式,直接从config.py读取最新配置,避免importlib.reload不确定性

#### 🎨 Web界面增强
- **可视化数据源选择**: 新增数据源选择界面,支持Keep和Garmin两种数据源的可视化切换
- **Garmin在线导入**: 在Web界面直接输入Garmin账户,一键抓取跑步数据(支持中国区/国际区账户)
- **测试登录功能**: 支持Garmin登录测试,验证账户可用性后再执行数据导入
- **导入结果反馈**: 实时显示导入统计(成功/失败条数),提供详细的操作反馈

#### 🗄️ 数据库架构优化
- **多数据源支持**: 新增`TrainingRecordManager`类,支持Keep和Garmin两种训练数据格式的动态切换
- **Garmin数据模型**: 新增`TrainingRecordGarmin`表,支持40+专业运动指标(心率区间、功率区间、步频步幅、训练负荷等)
- **字段映射系统**: 实现智能字段映射机制,自动适配不同数据源的字段差异(如Keep的`start_time` ↔ Garmin的`start_time_gmt`)
- **数据隔离**: Keep和Garmin数据存储在独立表中,互不干扰,支持独立统计视图

#### 🔌 API接口扩展
- **数据源管理**: 新增`/api/test_garmin_login`接口,支持Garmin账户登录测试
- **在线导入**: 新增`/api/import_garmin_data`接口,支持Garmin Connect在线数据抓取与导入
- **配置管理**: 优化`/api/save_config`接口,支持保存Garmin账户信息到配置文件
- **Excel上传**: 优化`/api/upload_training_excel`接口,统一使用新导入器架构

#### 📝 技术改进
- **向后兼容**: 保留`TrainingDataImporter = KeepDataImporter`别名,确保现有代码无缝迁移
- **错误处理**: 完善Garmin登录异常捕获,提供清晰的错误提示信息
- **代码简化**: 移除重复的数据库引擎创建逻辑,统一到BaseImporter基类中
- **导入模式**: 统一采用覆盖写入模式(truncate_first=True),避免数据重复

### 2025.12.8 - 训练数据导入功能修复
- **🔧 数据库连接修复**: 修复Excel训练数据导入时的数据库认证失败问题
- **⚡ 配置读取优化**: 移除不可靠的`importlib.reload()`机制,改为直接从config.py构建数据库引擎
- **✅ 稳定性提升**: TrainingDataImporter现在每次初始化都能准确读取最新的数据库配置,避免环境变量干扰
- **📊 Web上传保障**: 确保通过Web界面(/setup)上传Excel文件时的数据库连接稳定性
### 2025.12.8 - 可视化配置系统上线
- **🎨 可视化配置界面**: 新增Web可视化配置页面(`/setup`),支持LLM API、搜索API、MySQL数据库的可视化配置
- **✅ 智能健康检查**: 系统启动时自动运行8项健康检查,配置不完整时自动跳转到配置页面
- **🔧 实时连接测试**: 支持LLM API和MySQL连接的实时测试,配置前即可验证连接可用性
- **🗄️ 一键数据库初始化**: 点击按钮即可自动创建数据库和表结构,无需手动执行SQL脚本
- **📱 响应式设计**: 采用Morandi色系的现代化UI设计,横版布局一屏显示所有功能
- **⚠️ 重要提示**: 首次启动系统会自动重定向到配置页面,完成配置后才能正常使用

### 2025.12.8 - 配置管理重构
- **🔧 统一配置变量**: 将所有Agent的LLM配置统一为`LLM_API_KEY`、`LLM_BASE_URL`、`DEFAULT_MODEL_NAME`、`REPORT_MODEL_NAME`四个变量
- **📝 简化配置流程**: 除ReportAgent使用`qwen3-max`外，其他Agent统一使用`qwen-plus-latest`
- **⚠️ 重要提示**: 如果您之前使用旧版本配置，请参考[配置说明](#-配置说明)章节更新您的`config.py`文件

### 2025.12.8 - 数据库脚本修复
- 添加缺失的`training_tables.sql`，同时调整`import_traning_data.py`的文件路径，均放在`scripts`文件夹下

---

## 📖 项目简介

**Synapse Run** 是一款专为中长跑爱好者打造的智能训练助手系统,基于先进的多智能体协作架构设计。系统通过"论坛式"交互机制,让多个专业AI智能体像大脑神经突触(Synapse)一样协同工作、思维碰撞,为跑者提供专业、个性化的训练指导方案。

### 🎯 核心优势

- **🧠 多智能体协作架构**: 四个专业Agent通过论坛机制进行深度协作,避免单一模型的思维局限
- **📊 数据驱动训练分析**: 深度挖掘个人训练数据库(支持Keep数据导入),结合互联网专业资源,生成科学训练建议
- **🎨 智能报告生成**: 20+专业报告模板,动态选择最适合的模板,多轮优化生成高质量分析报告
- **🔌 纯Python轻量化设计**: 模块化架构,易于扩展和定制,支持任意OpenAI兼容的LLM接口

### ⚡ 技术栈

| 类别 | 技术 |
|------|------|
| **核心语言** | Python 3.9+ |
| **Web框架** | Flask (主应用) + Streamlit (调试界面) |
| **LLM接口** | OpenAI-compatible APIs (支持Qwen、Kimi、Gemini等) |
| **数据库** | MySQL 8.0+ |
| **网络工具** | Tavily API, Bocha Web Search |
| **前端** | HTML5, JavaScript, Socket.IO |

---

## 📚 前情提要

本项目基于著名开源项目"微舆"(BettaFish)改进而来,向原作者[@666ghj](https://github.com/666ghj)致以崇高敬意!

**原项目地址**: [666ghj/BettaFish: 微舆：人人可用的多Agent舆情分析助手](https://github.com/666ghj/BettaFish)

### 🔧 主要改进内容

针对中长跑训练场景进行了深度定制和优化:

| 改进类别 | 具体内容 |
|---------|---------|
| **领域适配** | 移除MindSpider爬虫、情感分析模块,专注训练数据分析 |
| **用户体验** | 全面升级UI界面,提供/training路由一键管理训练数据(支持Keep格式导入) |
| **搜索优化** | 优化Tavily搜索配置,添加中长跑专业网站白名单,提高搜索精准度 |
| **专业模板** | 新增20+中长跑专项报告模板(训练理论、营养补给、损伤康复等) |
| **API统一** | 全面更换为Qwen系列API,确保论坛协作响应速度一致性 |
| **提示词优化** | 各Agent提示词全面适配中长跑场景,注入动态时间防止LLM幻觉 |
| **数据库重构** | 全面调整InsightAgent中的数据库ORM与工具,完美适配中长跑训练数据结构 |
| **工具精简** | 简化QueryAgent工具调用,只保留deep_search_news专注学术文献检索,减少冗余 |
| **工具脚本** | 提供import_training_data.py(数据导入)、clear_reports.py(清空报告)等实用脚本 |

---

## 🏗️ 系统架构

### 多智能体协作架构

系统由四个核心Agent组成,每个Agent拥有独立的工具集、提示词模板和处理节点:

| Agent | 定位 | 核心工具 | 推荐模型 | 主要职责 |
|-------|------|---------|---------|---------|
| **Query Agent** | 理论专家 | Tavily API(新闻/网页搜索) | Qwen-Plus-Latest | 中长跑训练理论、学术文献检索、专业知识搜索 |
| **Media Agent** | 后勤情报官 | Bocha搜索、结构化数据卡片 | Qwen-Plus-Latest | 比赛报名、天气预报、装备价格、路线坡度等实用情报 |
| **Insight Agent** | 数据分析师 | 训练数据库查询工具 | Qwen-Plus-Latest | 历史训练数据挖掘、统计分析、趋势预测 |
| **Report Agent** | 报告生成器 | 模板选择引擎、HTML生成器 | Qwen3-Max | 智能选择模板、多轮优化报告、专业内容生成 |

### 🔄 系统架构图

系统的核心创新在于Agent间的"论坛式"协作机制,以下是完整的系统架构:

<div align="center">
<img src="static/image/architecture.png" alt="Synapse Run系统架构图" width="100%">
<p><i>Synapse Run多智能体协作架构 - 通过ForumEngine实现Agent间的思维碰撞与协同决策</i></p>
</div>

**核心工作机制**:
1. **用户提问** → Flask主应用接收训练问题
2. **并行启动** → 三个Agent(Query/Media/Insight)同时开始工作
3. **论坛协作** → 各Agent将分析结果写入`logs/forum.log`
4. **智能协调** → ForumEngine监控模块实时提取关键信息
5. **主持引导** → LLM主持人生成总结并引导下一步讨论方向
6. **交流融合** → 各Agent通过forum_reader工具读取论坛内容
7. **迭代优化** → 循环协作直到达成共识或任务完成
8. **报告生成** → Report Agent整合所有成果,生成专业训练报告

### 📊 完整工作流程

| 步骤 | 阶段名称 | 主要操作 | 参与组件 | 循环特性 |
|------|----------|----------|----------|----------|
| **1** | 用户提问 | 用户在Web界面输入训练问题 | Flask主应用 | - |
| **2** | 并行启动 | 三个Agent同时开始工作 | Query/Media/Insight Agent | - |
| **3** | 初步分析 | 各Agent使用专属工具进行概览搜索 | 各Agent + 专属工具集 | - |
| **4** | 策略制定 | 基于初步结果制定分块研究策略 | 各Agent内部决策模块 | - |
| **5-N** | **论坛协作循环** | **深度研究 + 论坛交流 + 方向调整** | **ForumEngine + 所有Agent** | **多轮循环** |
| **5.1** | 深度研究 | 各Agent基于论坛引导进行专项搜索 | 各Agent + 反思机制 | 每轮循环 |
| **5.2** | 论坛协作 | ForumEngine监控发言并生成主持人总结 | ForumEngine + LLM主持人 | 每轮循环 |
| **5.3** | 交流融合 | 各Agent根据讨论调整研究方向 | 各Agent + forum_reader工具 | 每轮循环 |
| **N+1** | 结果整合 | Report Agent收集所有分析结果和论坛内容 | Report Agent | - |
| **N+2** | 报告生成 | 动态选择模板,多轮优化生成最终报告 | Report Agent + 模板引擎 | - |

### 🧩 统一Agent架构模式

所有Agent遵循相同的模块化架构设计:

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

| 项目 | 要求 |
|------|------|
| **操作系统** | Windows / Linux / MacOS |
| **Python版本** | 3.9 或更高版本 |
| **包管理器** | Conda (推荐Anaconda或Miniconda) |
| **数据库** | MySQL 8.0+ |
| **内存** | 建议4GB以上 |
| **磁盘空间** | 至少2GB可用空间 |

### 📦 安装步骤

#### 1. 克隆项目

**从GitHub克隆**:
```bash
git clone https://github.com/zephyr4123/synapse-run.git
cd synapse-run
```

**或从Gitee克隆**:
```bash
git clone https://gitee.com/zephyr123_3/synapse-run.git
cd synapse-run
```

#### 2. 创建Conda环境

```bash
# 创建独立的Python环境
conda create -n synapse_run python=3.11
conda activate synapse_run
```

#### 3. 安装依赖包

```bash
# 安装所有依赖
pip install -r requirements.txt
```

#### 4. 配置系统

##### 4.1 配置API密钥

编辑项目根目录的 `config.py` 文件,填入您的API密钥:

```python
# ============================== 数据库配置 ==============================
DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "your_username"
DB_PASSWORD = "your_password"
DB_NAME = "traningData"  # 数据库名称
DB_CHARSET = "utf8mb4"

# ============================== LLM配置 ==============================
# 统一LLM配置 - 所有Agent共享相同的API Key和Base URL
# 申请地址: https://dashscope.aliyun.com/

# 统一API配置
LLM_API_KEY = "your_qwen_api_key"
LLM_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# 模型配置
DEFAULT_MODEL_NAME = "qwen-plus-latest"  # 用于: InsightEngine, MediaEngine, QueryEngine, ForumHost
REPORT_MODEL_NAME = "qwen3-max"          # 用于: ReportEngine (强编码能力)

# ============================== 网络工具配置 ==============================
# Tavily API (申请地址: https://www.tavily.com/)
TAVILY_API_KEY = "your_tavily_api_key"

# Bocha API (申请地址: https://open.bochaai.com/)
BOCHA_WEB_SEARCH_API_KEY = "your_bocha_api_key"
```

##### 4.2 初始化数据库

```bash
# 登录MySQL并创建数据库
mysql -u root -p

# 在MySQL命令行中执行
CREATE DATABASE traningData CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE traningData;
SOURCE scripts/training_tables.sql;
EXIT;
```

#### 5. 启动系统

##### 5.1 完整系统启动 (推荐)

```bash
# 激活conda环境
conda activate synapse_run

# 启动主应用
python app.py
```

系统启动后,在浏览器访问 **http://localhost:5000** 即可使用完整功能

##### 5.2 单Agent调试模式 (开发调试用)

```bash
# 启动Query Agent调试界面
streamlit run SingleEngineApp/query_engine_streamlit_app.py --server.port 8503

# 启动Media Agent调试界面
streamlit run SingleEngineApp/media_engine_streamlit_app.py --server.port 8502

# 启动Insight Agent调试界面
streamlit run SingleEngineApp/insight_engine_streamlit_app.py --server.port 8501
```

---

## 📂 项目结构

```
Synapse_Run/
├── QueryEngine/                   # 理论专家Agent
│   ├── agent.py                   # Agent主逻辑
│   ├── llms/base.py               # LLM接口封装
│   ├── nodes/                     # 处理节点(搜索/总结/格式化)
│   ├── tools/search.py            # Tavily搜索工具
│   ├── prompts/prompts.py         # 提示词模板
│   └── utils/config.py            # 配置管理
│
├── MediaEngine/                   # 后勤情报官Agent
│   ├── agent.py                   # Agent主逻辑
│   ├── llms/base.py               # LLM接口
│   ├── nodes/                     # 处理节点
│   ├── tools/search.py            # Bocha搜索工具
│   ├── prompts/prompts.py         # 提示词模板
│   └── utils/config.py            # 配置管理
│
├── InsightEngine/                 # 数据分析师Agent
│   ├── agent.py                   # Agent主逻辑
│   ├── llms/base.py               # LLM接口封装
│   ├── nodes/                     # 处理节点
│   ├── tools/search.py            # 数据库查询工具
│   ├── state/state.py             # 状态管理
│   ├── prompts/prompts.py         # 提示词模板
│   └── utils/config.py            # 配置管理
│
├── ReportEngine/                  # 报告生成器Agent
│   ├── agent.py                   # Agent主逻辑
│   ├── llms/base.py               # LLM接口
│   ├── nodes/                     # 报告生成节点
│   ├── report_template/           # 20+专业报告模板
│   │   ├── 训练理论与流派对比报告模板.md
│   │   ├── 营养补给与饮食策略报告模板.md
│   │   ├── 跑步损伤机制与康复报告模板.md
│   │   ├── 心率训练与配速控制报告模板.md
│   │   └── ... (共20+个专业模板)
│   └── flask_interface.py         # Flask API接口
│
├── ForumEngine/                   # 论坛引擎
│   ├── monitor.py                 # 日志监控和论坛管理
│   └── llm_host.py                # LLM主持人模块
│
├── routes/                        # Flask路由
│   └── training_data.py           # 训练数据管理路由(/training)
│
├── SingleEngineApp/               # 单Agent调试界面
│   ├── query_engine_streamlit_app.py
│   ├── media_engine_streamlit_app.py
│   └── insight_engine_streamlit_app.py
│
├── scripts/                       # 实用工具脚本
│   ├── import_training_data.py    # Keep数据导入脚本
│   └── clear_reports.py           # 清空报告脚本
│
├── templates/                     # Flask前端模板
│   └── index.html                 # 主界面
│
├── static/                        # 静态资源
│   └── image/                     # 图片资源
│       ├── logo.png               # 项目Logo
│       ├── finalResult.png        # 最终报告示例
│       ├── forumResult.png        # 论坛协作示例
│       ├── theoryExperResult.png  # 理论专家示例
│       ├── logisticsIntelligenceResult.png  # 情报官示例
│       └── sportScientistResult.png  # 数据分析示例
│
├── logs/                          # 运行日志目录
│
├── reports/                       # 生成的报告文件目录
│
├── utils/                         # 通用工具
│   ├── forum_reader.py            # Agent读取论坛工具
│   └── retry_helper.py            # 网络请求重试机制
│
├── schema/                        # 数据库Schema
│   └── training_tables.sql        # 训练数据表结构
│
├── app.py                         # Flask主应用入口
├── config.py                      # 全局配置文件
├── requirements.txt               # Python依赖清单
├── README.md                      # 中文说明文档
├── README-EN.md                   # 英文说明文档(待完善)
└── LICENSE                        # GPL-2.0许可证
```

---

## ⚙️ 自我适配指南

### 1. 调整MediaAgent地理位置提示词

编辑 `MediaEngine/prompts/prompts.py`,根据您的常用训练地点修改地理位置相关提示词:

```python
# 示例:将默认地理位置从"海口"改为"北京"
LOCATION_PROMPT = """
你是一位专业的跑步后勤情报官,主要服务于北京地区的跑者。
在搜索天气、路线、比赛等信息时,优先考虑北京及周边地区的资源。
"""
```

### 2. 导入个人训练数据 (Keep格式)

首次使用时,需要导入您的历史训练数据:

**步骤**:
1. 在Keep App中导出个人全部训练数据(格式:Excel)
2. 将导出的Excel文件重命名为 `training_data.xlsx`,放在项目data/目录下
3. 运行导入脚本:

```bash
python scripts/import_training_data.py
```

**后续管理**:
- 启动项目后,访问 **http://localhost:5000/training** 路由
- 在Web界面中可视化管理训练数据(增删改查)

### 3. 自定义报告模板

在 `ReportEngine/report_template/` 目录下创建您自己的Markdown模板:

```markdown
# {title} - 自定义报告模板

## 训练概况
{training_overview}

## 数据分析
{data_analysis}

## 专家建议
{expert_advice}

## 下一步行动计划
{action_plan}
```

模板变量说明:
- `{title}`: 报告标题
- `{training_overview}`: 训练概况
- `{data_analysis}`: 数据分析结果
- `{expert_advice}`: 专家建议
- `{action_plan}`: 行动计划

---

## 🔌 API使用指南

### LLM响应速度的重要性

**⚠️ 关键提示**: 论坛协作机制对各LLM响应速度极其敏感!

**问题**: 如果某个Agent的LLM响应过慢,会导致论坛的BrainStorm变成响应快的LLM一枝独秀,失去多智能体协作的优势。

**推荐配置**:

| Agent | 推荐模型 | 原因 |
|-------|---------|------|
| **Query Agent** | Qwen-Plus-Latest | 高速推理,保证搜索响应迅速 |
| **Media Agent** | Qwen-Plus-Latest | 高速推理,保证情报收集迅速 |
| **Insight Agent** | Qwen-Plus-Latest | 高速推理,保证数据分析迅速 |
| **Forum Host** | Qwen-Plus-Latest | 高速推理,保证论坛协调迅速 |
| **Report Agent** | Qwen3-Max / Kimi-K2 / GLM-4 | 可以慢一点,但需要强编码能力生成HTML报告 |

**原则**:
- 除了Report Agent,**统一使用高速推理的LLM** (推荐Qwen系列)
- 确保各Agent发言迅速,维持论坛活跃度
- Report Agent不受响应速度约束,可使用编码能力强的模型

### 支持的LLM厂商

只要兼容OpenAI调用格式的LLM都可以使用:

| 厂商 | 推荐模型 | 申请地址 |
|------|---------|---------|
| **阿里云DashScope** | Qwen-Plus-Latest, Qwen3-Max | https://dashscope.aliyun.com/ |
| **Moonshot AI** | Kimi-K2 | https://platform.moonshot.cn/ |
| **Google Gemini** | Gemini-2.0-Flash-Exp | https://ai.google.dev/ |
| **智谱AI** | GLM-4, GLM-4-Plus | https://open.bigmodel.cn/ |
| **DeepSeek** | DeepSeek-Chat | https://platform.deepseek.com/ |

---

## 📸 效果展示

### 论坛协作过程

<div align="center">
<img src="static/image/forumResult.png" alt="论坛协作示例" width="90%">
<p><i>多个Agent通过论坛机制进行思维碰撞与协作</i></p>
</div>

### 理论专家Agent工作示例

<div align="center">
<img src="static/image/theoryExperResult.png" alt="理论专家工作示例" width="90%">
<p><i>Query Agent搜索中长跑训练理论与学术文献</i></p>
</div>

### 后勤情报官Agent工作示例

<div align="center">
<img src="static/image/logisticsIntelligenceResult.png" alt="情报官工作示例" width="90%">
<p><i>Media Agent收集比赛、天气、装备等实用情报</i></p>
</div>

### 数据分析师Agent工作示例

<div align="center">
<img src="static/image/sportScientistResult.png" alt="数据分析示例" width="90%">
<p><i>Insight Agent深度挖掘历史训练数据</i></p>
</div>

### 训练数据管理后台

<div align="center">
<img src="static/image/runTrack.png" alt="训练数据管理界面" width="90%">
<p><i>/training路由 - 可视化管理个人训练数据,支持Keep数据导入与CRUD操作</i></p>
</div>

### 最终智能报告

<div align="center">
<img src="static/image/finalResult.png" alt="最终报告示例" width="90%">
<p><i>Report Agent生成的专业训练分析报告</i></p>
</div>

---

## 🔧 扩展建议

### InsightAgent数据源扩展

**当前限制**:

目前项目中的InsightAgent严格遵循Keep的导出格式,存在以下泛化性问题:
- **格式依赖强**: 仅支持Keep的Excel导出格式,其他运动应用数据需手动转换
- **手动维护**: 每次导入新数据都需要在 `/training` 路由手动添加,无法自动化同步

**扩展建议**:

考虑使用 **Garmin Connect API** 实现自动化数据同步:

| 方案 | 优点 | 挑战 |
|------|------|------|
| **Garmin API集成** | - 自动同步训练数据<br>- 支持更丰富的运动指标(心率变异性、训练负荷等)<br>- 无需手动导入 | - 需要Garmin账号授权<br>- API调用可能受网络限制<br>- 需处理OAuth认证流程 |

**实现思路**:

1. **API认证**: 集成Garmin Connect OAuth 2.0认证流程
2. **数据同步**: 定时任务(Cron/Celery)自动拉取新训练数据
3. **数据转换**: 将Garmin API返回的JSON格式转换为系统数据库Schema
4. **增量更新**: 仅同步新增数据,避免重复导入

**作者说明**:

由于不可控的网络因素(GFW等),作者无法稳定访问Garmin Connect API,原生直接实现较为困难,可能需要通过API代理或中转服务实现。**有兴趣的伙伴可以基于此思路自行扩展**,欢迎提交PR!

**其他可扩展数据源**:
- 🏃 **Nike Run Club**: 通过逆向工程其移动应用API
- 🏃 **Strava**: 官方API支持完善,适合集成
- 🏃 **悦跑圈**: 国内主流跑步应用,可尝试数据导出
- 🏃 **咕咚运动**: 支持数据导出功能

---

## 🙏 致谢

本项目的诞生离不开开源社区的支持,特别要向 **BettaFish(微舆)** 项目及其作者 [@666ghj](https://github.com/666ghj) 表达崇高的敬意!

**为什么致敬BettaFish?**

BettaFish项目展示了多智能体协作架构在舆情分析领域的强大潜力,其创新的"论坛式"Agent交互机制、模块化的系统设计、以及对代码质量的极致追求,为我们提供了宝贵的参考范例。作者在项目中展现的工程实践水平和开源精神,令人钦佩!

**Synapse Run = BettaFish的中长跑领域适配版本**

我们基于BettaFish的核心架构,针对中长跑训练场景进行了深度定制,希望能将这种先进的多智能体协作理念带到更多垂直领域,让AI真正成为每个人的智能助手。

**再次感谢BettaFish项目的开源贡献!** 🎉

---

## 📄 许可证

本项目采用 **GPL-2.0 许可证** 开源。

这意味着:
- ✅ 您可以自由使用、修改和分发本项目
- ✅ 您可以将本项目用于商业目的
- ⚠️ 如果您分发修改后的版本,必须同样以GPL-2.0许可证开源
- ⚠️ 您必须在修改后的代码中保留原始版权声明

详细信息请参阅 [LICENSE](LICENSE) 文件。

---

## 📧 联系方式

如有任何问题、建议或合作意向,欢迎通过以下方式联系我们:

- **📮 邮箱**: huangsuxiang5@gmail.com
- **💬 微信**: 13976457218
- **🐧 QQ**: 1736672988

**我们期待与您交流!** 💬

---

<div align="center">

### 让AI成为你的智能跑步教练 🏃‍♂️

**Made with ❤️ by Synapse Run Team**

⭐ 如果这个项目对你有帮助,请给我们一个Star! ⭐

</div>
