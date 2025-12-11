<div align="center">

<img src="static/image/logo.png" alt="Synapse Run Logo" width="100%">

# Synapse Run

**智能跑步训练助手 | 多智能体协作系统**

[![License: GPL v2](https://img.shields.io/badge/License-GPL%20v2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html) [![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/) [![Version](https://img.shields.io/badge/version-1.0.0-brightgreen.svg)](https://github.com/zephyr4123/synapse-run)

[English](./README-EN.md) | [中文文档](./README.md) | [更新日志](./docs/updateLog.md)

</div>

---

## 🎉 v1.0.0 正式版更新说明

**发布日期**: 2025年12月11日

### ✨ 重大更新

1. **🏃 扩展佳明(Garmin)数据支持**: 完全兼容Garmin Connect数据源,保持可扩展性,便于后续接入更多运动平台
2. **🎨 可视化配置界面**: 首次使用提供健康检查与可视化配置流程,无需手动编辑config.py,一键配置API密钥与数据库
3. **📊 智能数据源适配**: 根据`TRAINING_DATA_SOURCE`配置动态调整LLM提示词与工具集(Garmin拥有更丰富的生理指标工具)
4. **📈 双数据后台支持**: `/training`监控页面支持Keep与Garmin两种模式
   - **Keep模式**: 提供增删改查功能,手动管理训练数据
   - **Garmin模式**: 一键同步按钮,自动从Garmin Connect拉取最新数据

### 🔧 配置优化

- 简化数据导入流程,支持Excel导入(Keep)与邮箱授权同步(Garmin)
- 优化健康检查机制,启动时自动检测API与数据库配置
- 增强错误提示,配置失败时提供详细指引

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

### 前置准备

在开始使用Synapse Run之前,请确保完成以下准备工作:

#### 【1】环境配置

| 环境 | 要求 | 安装教程 |
|------|------|---------|
| **VSCode** | 最新稳定版 | [安装教程](https://blog.csdn.net/qq_52102933/article/details/120387246) |
| **MySQL** | 8.0+ | [安装教程](https://blog.csdn.net/2509_94228395/article/details/155399232) |
| **Git** | 最新版(可选) | [安装教程](https://blog.csdn.net/mukes/article/details/115693833) |
| **Python** | 3.9+ | 推荐使用Conda环境管理 |

#### 【2】申请API密钥

| API服务 | 用途 | 申请地址 |
|---------|------|---------|
| **阿里云大模型API** | 核心LLM服务 | https://dashscope.aliyun.com/ |
| **Tavily搜索API** | 学术文献与理论检索 | https://www.tavily.com/ |
| **Bocha爬虫API** | 实用情报收集(需购买ai_search版本) | https://open.bochaai.com/ |

⚠️ **注意**: Bocha API必须购买**ai_search版本**,web_search版本不适用于本系统

#### 【3】数据准备

根据您使用的运动追踪设备选择对应的数据准备方式:

**📱 Keep用户**:
1. 打开Keep App
2. 进入 `设置` → `个人收集清单` → `个人信息下载`
3. 填写接收邮箱
4. 等待约10分钟,完整Excel表格将发送到您的邮箱

<div align="center">
<img src="static/image/keepEmail.png" alt="Keep数据导出邮件" width="60%">
<p><i>Keep数据导出邮件示例</i></p>
</div>

**⌚ Garmin用户**:
- 准备好您的Garmin Connect账号邮箱与密码
- 无需额外准备,系统将自动同步数据

---

### 📦 部署流程

#### 1️⃣ 克隆项目

```bash
# 从GitHub克隆(推荐)
git clone https://github.com/zephyr4123/synapse-run.git
cd synapse-run

# 或从Gitee克隆(国内镜像)
git clone https://gitee.com/zephyr123_3/synapse-run.git
cd synapse-run

# 或直接下载压缩包解压
```

#### 2️⃣ 安装依赖

```bash
# 如果使用Conda环境(推荐)
conda create -n synapse_run python=3.11
conda activate synapse_run
pip install -r requirements.txt

# 或使用系统Python
pip install -r requirements.txt
```

#### 3️⃣ 启动系统

```bash
# 激活环境(如使用Conda)
conda activate synapse_run

# 启动主应用
python app.py
```

启动后,浏览器会自动打开 **http://localhost:5000**

---

### 🎯 初次使用配置

#### 【1】健康检查

首次启动时,系统会自动进行健康检查。如果检测到配置缺失或错误,会自动跳转到配置界面:

<div align="center">
<img src="static/image/healthCheck.png" alt="系统健康检查" width="80%">
<p><i>系统健康检查 - 自动检测API与数据库配置</i></p>
</div>

#### 【2】可视化配置

**配置API密钥**:

<div align="center">
<img src="static/image/apiSetting.png" alt="API配置界面" width="80%">
<p><i>一键配置所有API密钥</i></p>
</div>

**配置MySQL数据库**:

<div align="center">
<img src="static/image/databaseSetting.png" alt="数据库配置界面" width="80%">
<p><i>可视化配置MySQL连接信息</i></p>
</div>

⚠️ **重要**:
- 配置完成后务必点击 **"保存配置"** 按钮
- 如需手动调整配置或修改高级参数,请直接编辑项目根目录的 `config.py` 文件

#### 【3】选择数据源并导入

配置保存后,系统会在3秒内自动跳转回健康检查页面。如果检查通过,点击 **"导入训练数据"** 按钮:

<div align="center">
<img src="static/image/jumpToImportData.png" alt="跳转导入数据" width="80%">
<p><i>健康检查通过后的导入入口</i></p>
</div>

**选择您的数据源类型**:

<div align="center">
<img src="static/image/dataSourceSelect.png" alt="选择数据源" width="80%">
<p><i>支持Keep与Garmin两种数据源</i></p>
</div>

**Keep用户导入流程**:
1. 选择 "Keep" 数据源
2. 上传从邮箱下载的Excel表格
3. 等待导入完成

<div align="center">
<img src="static/image/keepImportSuccess.png" alt="Keep导入成功" width="80%">
<p><i>Keep数据导入成功提示</i></p>
</div>

**Garmin用户导入流程**:
1. 选择 "Garmin" 数据源
2. 输入Garmin Connect邮箱与密码
3. 系统自动同步历史训练数据

<div align="center">
<img src="static/image/garminImportSuccess.png" alt="Garmin导入成功" width="80%">
<p><i>Garmin数据同步成功提示</i></p>
</div>

导入完成后,即可进入系统开始使用!

---

### 📊 训练数据后台管理

在主界面右上角,或直接访问 **http://localhost:5000/training** 进入数据监控后台。

**Garmin用户后台** (简洁模式):

<div align="center">
<img src="static/image/garminDataMonitor.png" alt="Garmin数据后台" width="80%">
<p><i>Garmin数据后台 - 一键同步最新训练数据</i></p>
</div>

- 点击右上角 **"同步Garmin数据"** 按钮即可实时同步最新训练记录
- 无需手动添加或管理数据

**Keep用户后台** (完整CRUD):

<div align="center">
<img src="static/image/keepDataMonitor.png" alt="Keep数据后台" width="80%">
<p><i>Keep数据后台 - 支持增删改查操作</i></p>
</div>

- 提供完整的增删改查功能
- 由于Keep生态封闭,需手动同步数据(无法频繁导出Excel)
- 支持单条记录的添加、编辑、删除操作

---

### 🛠️ 单Agent调试模式 (开发者选项)

如需单独调试某个Agent,可使用Streamlit调试界面:

```bash
# 启动Query Agent (理论专家)
streamlit run SingleEngineApp/query_engine_streamlit_app.py --server.port 8503

# 启动Media Agent (后勤情报官)
streamlit run SingleEngineApp/media_engine_streamlit_app.py --server.port 8502

# 启动Insight Agent (数据分析师)
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
│   ├── tools/                     # Tavily搜索工具
│   ├── prompts/prompts.py         # 提示词模板
│   ├── state/state.py             # 状态管理
│   └── utils/config.py            # 配置管理
│
├── MediaEngine/                   # 后勤情报官Agent
│   ├── agent.py                   # Agent主逻辑
│   ├── llms/base.py               # LLM接口
│   ├── nodes/                     # 处理节点
│   ├── tools/                     # Bocha搜索工具
│   ├── prompts/prompts.py         # 提示词模板
│   ├── state/state.py             # 状态管理
│   └── utils/config.py            # 配置管理
│
├── InsightEngine/                 # 数据分析师Agent
│   ├── agent.py                   # Agent主逻辑
│   ├── llms/base.py               # LLM接口封装
│   ├── nodes/                     # 处理节点
│   ├── tools/                     # 数据库查询工具(Keep/Garmin)
│   ├── prompts/                   # 提示词模板与工具描述
│   ├── state/state.py             # 状态管理
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
│   │   └── ... (共20+个专业模板)
│   ├── prompts/prompts.py         # 提示词模板
│   ├── state/state.py             # 状态管理
│   └── utils/config.py            # 配置管理
│
├── ForumEngine/                   # 论坛引擎
│   ├── monitor.py                 # 日志监控和论坛管理
│   └── llm_host.py                # LLM主持人模块
│
├── routes/                        # Flask路由模块
│   ├── routes/                    # 子路由目录
│   ├── utils/                     # 路由工具函数
│   ├── setup.py                   # 设置页面路由
│   └── training_data.py           # 训练数据管理路由
│
├── SingleEngineApp/               # 单Agent调试界面
│   ├── query_engine_streamlit_app.py    # Query Agent调试
│   ├── media_engine_streamlit_app.py    # Media Agent调试
│   └── insight_engine_streamlit_app.py  # Insight Agent调试
│
├── scripts/                       # 实用工具脚本
│   ├── training_data_importer.py  # 训练数据导入器
│   ├── training_tables.sql        # 数据库表结构
│   └── clear_reports.sh           # 清空报告脚本
│
├── templates/                     # Flask前端模板
│   ├── index.html                 # 主界面
│   ├── setup.html                 # 配置页面
│   ├── training_data.html         # Keep数据后台
│   └── training_data_garmin.html  # Garmin数据后台
│
├── static/                        # 静态资源
│   ├── image/                     # 图片资源
│   │   ├── logo.png               # 项目Logo
│   │   ├── finalResult.png        # 最终报告示例
│   │   ├── forumResult.png        # 论坛协作示例
│   │   ├── healthCheck.png        # 健康检查界面
│   │   ├── apiSetting.png         # API配置界面
│   │   ├── databaseSetting.png    # 数据库配置界面
│   │   └── ... (更多截图)
│   └── js/                        # JavaScript文件
│
├── utils/                         # 通用工具模块
│   ├── forum_reader.py            # Agent读取论坛工具
│   ├── retry_helper.py            # 网络请求重试机制
│   ├── time_helper.py             # 时间处理工具
│   ├── health_check.py            # 系统健康检查
│   └── config_reloader.py         # 配置热重载
│
├── logs/                          # 运行日志目录
│   └── forum.log                  # 论坛交流日志
│
├── reports/                       # Web生成的报告文件
├── final_reports/                 # 最终报告存储目录
├── *_streamlit_reports/           # Streamlit调试报告目录
├── data/                          # 临时数据目录
├── docs/                          # 文档目录
├── models/                        # 训练记录ORM模型
│
├── app.py                         # Flask主应用入口
├── config.py                      # 全局配置文件
├── requirements.txt               # Python依赖清单
├── README.md                      # 中文说明文档
├── README-EN.md                   # 英文说明文档
└── .gitignore                     # Git忽略配置
```

**注意**:
- `logs/`、`reports/`、`data/` 目录下的文件不会被Git追踪(已在.gitignore中配置)
- `*_streamlit_reports/` 为Streamlit调试模式生成的临时报告目录

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

### 2. 切换数据源

系统支持Keep与Garmin两种数据源,可在 `config.py` 中配置:

```python
# 训练数据源配置
TRAINING_DATA_SOURCE = "garmin"  # 可选: "keep" 或 "garmin"
```

**数据源对比**:

| 特性 | Keep | Garmin |
|------|------|--------|
| **数据导入** | 手动上传Excel | 自动同步(邮箱授权) |
| **数据更新** | 手动添加 | 一键同步 |
| **数据丰富度** | 基础训练指标 | 高级生理指标(心率变异性、训练负荷等) |
| **后台管理** | 完整CRUD | 只读+同步按钮 |

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

### 最终智能报告

<div align="center">
<img src="static/image/finalResult.png" alt="最终报告示例" width="90%">
<p><i>Report Agent生成的专业训练分析报告</i></p>
</div>

---

## 🔧 扩展建议

### InsightAgent数据源扩展

**✅ 已支持数据源**: Keep、Garmin Connect

**🚀 可扩展数据源**:

系统采用模块化设计,易于接入更多运动平台数据:

| 数据源 | 集成难度 | API支持 | 推荐度 |
|--------|---------|---------|--------|
| **Strava** | ⭐⭐ | 官方API完善 | ⭐⭐⭐⭐⭐ |
| **Nike Run Club** | ⭐⭐⭐⭐ | 需逆向工程 | ⭐⭐⭐ |
| **悦跑圈** | ⭐⭐⭐ | 数据导出支持 | ⭐⭐⭐ |
| **咕咚运动** | ⭐⭐⭐ | 数据导出支持 | ⭐⭐⭐ |
| **Apple Health** | ⭐⭐ | 导出XML格式 | ⭐⭐⭐⭐ |

**扩展步骤**:

1. **数据源适配器开发** (`InsightEngine/tools/`):
   ```python
   class StravaDataAdapter:
       def fetch_activities(self, access_token):
           # 调用Strava API获取训练数据
           pass

       def convert_to_schema(self, strava_data):
           # 转换为系统数据库Schema
           pass
   ```

2. **配置文件更新** (`config.py`):
   ```python
   TRAINING_DATA_SOURCE = "strava"  # 新增数据源选项
   STRAVA_CLIENT_ID = "your_client_id"
   STRAVA_CLIENT_SECRET = "your_client_secret"
   ```

3. **后台界面扩展** (`routes/training_data.py`):
   - 添加Strava授权按钮
   - 实现数据同步接口

**欢迎社区贡献**: 如果您成功集成了新的数据源,欢迎提交PR分享给社区!

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
