<div align="center">

<img src="static/image/logo.png" alt="Synapse Run Logo" width="100%">

# Synapse Run

**Intelligent Running Training Assistant | Multi-Agent Collaborative System**

[![License: GPL v2](https://img.shields.io/badge/License-GPL%20v2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html) [![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/) [![Version](https://img.shields.io/badge/version-1.0.1-brightgreen.svg)](https://github.com/zephyr4123/synapse-run)

[English](./README-EN.md) | [中文文档](./README.md) | [Changelog](./docs/updateLog.md)

</div>

---

## ⚠️ Linux Deployment Critical Notice

**Issue**: When using Garmin Connect login on Linux environments, you may encounter `ValueError: duplicate parameter name: 'timestamp_gmt'` error.

**Cause**: The `garth` library (a dependency of `garminconnect`) has a duplicate parameter name issue, causing Pydantic dataclass signature generation to fail.

**Solution**:
1. Locate the dependency library file (adjust path based on your environment):
   ```bash
   nano <YOUR_ENV_PATH>/lib/python3.11/site-packages/garth/data/weight.py
   ```

2. Around line 17, find the following code:
   ```python
   datetime_utc: datetime = Field(..., alias="timestamp_gmt")
   ```

3. Modify it to:
   ```python
   datetime_utc: datetime = Field(..., alias="timestamp_gmt_datetime")  # Change to a different alias to avoid duplication
   ```

4. Save the file and restart the program to use Garmin Connect normally.

> 💡 **Tip**: This is a known issue in the dependency library. The fix does not affect Garmin Connect's normal functionality. If you encounter permission issues, use `sudo` or switch to a user with write permissions.

---

## 🎉 v1.0.1 Release Notes

**Release Date**: 16th December 2025

### 🐛 Bug Fixes

**Special thanks to community contributor [@JacobZang](https://github.com/JacobZang) for the PR fix!**

- **Fixed Garmin Data Sync Issue**: Fixed the problem where the system did not properly prioritize the `is_cn` parameter passed from the frontend when syncing Garmin data
  - **Issue Description**: The system did not prioritize the region parameter passed from the frontend during Garmin data synchronization, which could cause users in different regions to access the wrong Garmin server
  - **Fix Solution**: Optimized parameter passing logic to ensure the frontend's `is_cn` parameter is correctly used in the sync process
  - **Impact Scope**: All users using Garmin data source
  - **Contributor**: [@JacobZang](https://github.com/JacobZang)

### 🙏 Special Thanks

Thanks to [@JacobZang](https://github.com/JacobZang) for discovering and fixing this issue that affected Garmin user experience! This is the first community PR our project has received, and we are very grateful for your contribution! 🎉

---

## 🎉 v1.0.0 Official Release

**Release Date**: 11th December 2025 

### ✨ Major Updates

1. **🏃 Extended Garmin Data Support**: Fully compatible with Garmin Connect data source, maintaining extensibility for future integration of more data sources
2. **🎨 Visual Configuration Interface**: First-time use provides health check and visual configuration process, no need to manually edit config.py, one-click configuration of API keys and database
3. **📊 Intelligent Data Source Adaptation**: Dynamically adjusts LLM prompts and toolsets based on `TRAINING_DATA_SOURCE` configuration (Garmin has richer tools with more physiological metrics)
4. **📈 Dual Data Backend Support**: `/training` monitoring page supports both Keep and Garmin modes
   - **Keep Mode**: Provides full CRUD functionality, manually manage training data
   - **Garmin Mode**: One-click sync button, automatically pulls latest data from Garmin Connect

### 🔧 Configuration Optimization

- Simplified data import process, supports Excel import (Keep) and email authorization sync (Garmin)
- Optimized health check mechanism, automatically detects API and database configuration at startup
- Enhanced error prompts, provides detailed guidance when configuration fails

---

## 📖 Project Overview

**Synapse Run** is an intelligent training assistant system designed specifically for middle and long-distance running enthusiasts, built on an advanced multi-agent collaborative architecture. Through a "forum-style" interaction mechanism, the system enables multiple professional AI agents to work together and brainstorm like brain synapses, providing runners with professional and personalized training guidance.

### 🎯 Core Advantages

- **🧠 Multi-Agent Collaborative Architecture**: Four professional agents collaborate deeply through a forum mechanism, avoiding the limitations of single-model thinking
- **📊 Data-Driven Training Analysis**: Deep mining of personal training database (supports Keep & Garmin data), combined with professional internet resources, generates scientific training recommendations
- **🎨 Intelligent Report Generation**: 20+ professional report templates, dynamically selecting the most suitable template, multi-round optimization for high-quality analytical reports
- **🔌 Pure Python Lightweight Design**: Modular architecture, easy to extend and customize, supports any OpenAI-compatible LLM interface

### ⚡ Technology Stack

| Category | Technology |
|----------|-----------|
| **Core Language** | Python 3.9+ |
| **Web Framework** | Flask (main app) + Streamlit (debug interface) |
| **LLM Interface** | OpenAI-compatible APIs (supports Qwen, Kimi, Gemini, etc.) |
| **Database** | MySQL 8.0+ |
| **Network Tools** | Tavily API, Bocha Web Search |
| **Frontend** | HTML5, JavaScript, Socket.IO |

---

## 📚 Background

This project is an improved version based on the famous open-source project "微舆" (BettaFish). We pay our highest respect to the original author [@666ghj](https://github.com/666ghj)!

**Original Project**: [666ghj/BettaFish: 微舆：人人可用的多Agent舆情分析助手](https://github.com/666ghj/BettaFish)

### 🔧 Main Improvements

Deeply customized and optimized for middle and long-distance running training scenarios:

| Category | Specific Content |
|----------|------------------|
| **Domain Adaptation** | Removed MindSpider crawler and sentiment analysis modules, focused on training data analysis |
| **User Experience** | Comprehensively upgraded UI interface, provided /training route for one-click training data management (supports Keep & Garmin) |
| **Search Optimization** | Optimized Tavily search configuration, added whitelist of professional running websites, improved search accuracy |
| **Professional Templates** | Added 20+ specialized running report templates (training theory, nutrition, injury recovery, etc.) |
| **API Unification** | Fully replaced with Qwen series APIs to ensure consistency in forum collaboration response speed |
| **Prompt Optimization** | All agent prompts fully adapted to running scenarios, injected dynamic time to prevent LLM hallucination |
| **Database Refactoring** | Comprehensively adjusted database ORM and tools in InsightAgent, perfectly adapted to running training data structure |
| **Tool Simplification** | Simplified QueryAgent tool calls, only retained deep_search_news for academic literature retrieval, reduced redundancy |
| **Utility Scripts** | Provided training_data_importer.py (data import), clear_reports.sh (clear reports) and other utility scripts |

---

## 🏗️ System Architecture

### Multi-Agent Collaborative Architecture

The system consists of four core agents, each with independent toolsets, prompt templates, and processing nodes:

| Agent | Role | Core Tools | Recommended Model | Main Responsibilities |
|-------|------|-----------|------------------|----------------------|
| **Query Agent** | Theory Expert | Tavily API (news/web search) | Qwen-Plus-Latest | Running training theory, academic literature retrieval, professional knowledge search |
| **Media Agent** | Logistics Intelligence | Bocha search, structured data cards | Qwen-Plus-Latest | Race registration, weather forecast, equipment prices, route slopes and other practical intelligence |
| **Insight Agent** | Data Analyst | Training database query tools (Keep/Garmin) | Qwen-Plus-Latest | Historical training data mining, statistical analysis, trend prediction |
| **Report Agent** | Report Generator | Template selection engine, HTML generator | Qwen3-Max | Intelligent template selection, multi-round report optimization, professional content generation |

### 🔄 System Architecture Diagram

The core innovation of the system lies in the "forum-style" collaboration mechanism between agents. Here is the complete system architecture:

<div align="center">
<img src="static/image/architecture.png" alt="Synapse Run System Architecture" width="100%">
<p><i>Synapse Run Multi-Agent Collaborative Architecture - Achieving brainstorming and collaborative decision-making between agents through ForumEngine</i></p>
</div>

**Core Working Mechanism**:
1. **User Question** → Flask main application receives training questions
2. **Parallel Start** → Three agents (Query/Media/Insight) start working simultaneously
3. **Forum Collaboration** → Each agent writes analysis results to `logs/forum.log`
4. **Intelligent Coordination** → ForumEngine monitoring module extracts key information in real-time
5. **Host Guidance** → LLM host generates summary and guides the next discussion direction
6. **Communication Fusion** → Each agent reads forum content through forum_reader tool
7. **Iterative Optimization** → Loop collaboration until consensus is reached or task is completed
8. **Report Generation** → Report Agent integrates all results and generates professional training reports

### 📊 Complete Workflow

| Step | Stage Name | Main Operations | Participating Components | Loop Characteristics |
|------|-----------|----------------|-------------------------|---------------------|
| **1** | User Question | User inputs training question in web interface | Flask main app | - |
| **2** | Parallel Start | Three agents start working simultaneously | Query/Media/Insight Agent | - |
| **3** | Initial Analysis | Each agent uses exclusive tools for overview search | Each agent + exclusive toolset | - |
| **4** | Strategy Formulation | Formulate block research strategy based on initial results | Each agent's internal decision module | - |
| **5-N** | **Forum Collaboration Loop** | **Deep Research + Forum Communication + Direction Adjustment** | **ForumEngine + All Agents** | **Multi-round Loop** |
| **5.1** | Deep Research | Each agent conducts specialized search based on forum guidance | Each agent + reflection mechanism | Each loop |
| **5.2** | Forum Collaboration | ForumEngine monitors speeches and generates host summary | ForumEngine + LLM host | Each loop |
| **5.3** | Communication Fusion | Each agent adjusts research direction based on discussion | Each agent + forum_reader tool | Each loop |
| **N+1** | Result Integration | Report Agent collects all analysis results and forum content | Report Agent | - |
| **N+2** | Report Generation | Dynamically select template, multi-round optimization to generate final report | Report Agent + template engine | - |

### 🧩 Unified Agent Architecture Pattern

All agents follow the same modular architecture design:

```
<Agent>/
├── agent.py              # Agent main class, implementing complete workflow
├── llms/base.py          # Unified OpenAI-compatible LLM client
├── nodes/                # Processing nodes
│   ├── base_node.py      # Base node class
│   ├── search_node.py    # Search node
│   ├── summary_node.py   # Summary node
│   └── formatting_node.py # Formatting node
├── tools/                # Exclusive toolset
├── state/state.py        # Agent state management
├── prompts/prompts.py    # Prompt templates
└── utils/config.py       # Configuration management
```

---

## 🚀 Quick Start

### Prerequisites

Before starting to use Synapse Run, please ensure the following preparations are completed:

#### 【1】Environment Configuration

| Environment | Requirement | Installation Tutorial |
|------------|------------|---------------------|
| **VSCode** | Latest stable version | [Tutorial](https://blog.csdn.net/qq_52102933/article/details/120387246) |
| **MySQL** | 8.0+ | [Tutorial](https://blog.csdn.net/2509_94228395/article/details/155399232) |
| **Git** | Latest version (optional) | [Tutorial](https://blog.csdn.net/mukes/article/details/115693833) |
| **Python** | 3.9+ | Recommended to use Conda environment management |

#### 【2】Apply for API Keys

| API Service | Purpose | Application URL |
|------------|---------|----------------|
| **Alibaba Cloud LLM API** | Core LLM service | https://dashscope.aliyun.com/ |
| **Tavily Search API** | Academic literature & theory retrieval | https://www.tavily.com/ |
| **Bocha Crawler API** | Practical intelligence collection (must purchase ai_search version) | https://open.bochaai.com/ |

⚠️ **Note**: Bocha API must purchase **ai_search version**, web_search version is not applicable to this system

#### 【3】Data Preparation

Choose the corresponding data preparation method according to your sports tracking device:

**📱 Keep Users**:
1. Open Keep App
2. Go to `Settings` → `Personal Collection List` → `Personal Information Download`
3. Fill in receiving email
4. Wait about 10 minutes, complete Excel table will be sent to your email

<div align="center">
<img src="static/image/keepEmail.png" alt="Keep Data Export Email" width="60%">
<p><i>Keep Data Export Email Example</i></p>
</div>

**⌚ Garmin Users**:
- Prepare your Garmin Connect account email and password
- No additional preparation needed, system will automatically sync data

---

### 📦 Deployment Process

#### 1️⃣ Clone Project

```bash
# Clone from GitHub (recommended)
git clone https://github.com/zephyr4123/synapse-run.git
cd synapse-run

# Or clone from Gitee (domestic mirror)
git clone https://gitee.com/zephyr123_3/synapse-run.git
cd synapse-run

# Or directly download compressed package and extract
```

#### 2️⃣ Install Dependencies

```bash
# If using Conda environment (recommended)
conda create -n synapse_run python=3.11
conda activate synapse_run
pip install -r requirements.txt

# Or use system Python
pip install -r requirements.txt
```

#### 3️⃣ Start System

```bash
# Activate environment (if using Conda)
conda activate synapse_run

# Start main application
python app.py
```

After startup, browser will automatically open **http://localhost:5000**

---

### 🎯 First-Time Use Configuration

#### 【1】Health Check

On first startup, the system will automatically perform a health check. If configuration is missing or incorrect, it will automatically redirect to the configuration page:

<div align="center">
<img src="static/image/healthCheck.png" alt="System Health Check" width="80%">
<p><i>System Health Check - Automatically detect API and database configuration</i></p>
</div>

#### 【2】Visual Configuration

**Configure API Keys**:

<div align="center">
<img src="static/image/apiSetting.png" alt="API Configuration Interface" width="80%">
<p><i>One-click configuration of all API keys</i></p>
</div>

**Configure MySQL Database**:

<div align="center">
<img src="static/image/databaseSetting.png" alt="Database Configuration Interface" width="80%">
<p><i>Visual configuration of MySQL connection information</i></p>
</div>

⚠️ **Important**:
- Be sure to click the **"Save Configuration"** button after configuration
- If you need to manually adjust configuration or modify advanced parameters, please directly edit the `config.py` file in the project root directory

#### 【3】Select Data Source and Import

After saving configuration, the system will automatically redirect to the health check page within 3 seconds. If the check passes, click the **"Import Training Data"** button:

<div align="center">
<img src="static/image/jumpToImportData.png" alt="Jump to Import Data" width="80%">
<p><i>Import entry after health check passes</i></p>
</div>

**Select Your Data Source Type**:

<div align="center">
<img src="static/image/dataSourceSelect.png" alt="Select Data Source" width="80%">
<p><i>Supports both Keep and Garmin data sources</i></p>
</div>

**Keep User Import Process**:
1. Select "Keep" data source
2. Upload Excel table downloaded from email
3. Wait for import to complete

<div align="center">
<img src="static/image/keepImportSuccess.png" alt="Keep Import Success" width="80%">
<p><i>Keep Data Import Success Prompt</i></p>
</div>

**Garmin User Import Process**:
1. Select "Garmin" data source
2. Enter Garmin Connect email and password
3. System automatically syncs historical training data

<div align="center">
<img src="static/image/garminImportSuccess.png" alt="Garmin Import Success" width="80%">
<p><i>Garmin Data Sync Success Prompt</i></p>
</div>

After import is complete, you can enter the system and start using it!

---

### 📊 Training Data Backend Management

In the upper right corner of the main interface, or directly access **http://localhost:5000/training** to enter the data monitoring backend.

**Garmin User Backend** (Simple Mode):

<div align="center">
<img src="static/image/garminDataMonitor.png" alt="Garmin Data Backend" width="80%">
<p><i>Garmin Data Backend - One-click sync latest training data</i></p>
</div>

- Click the **"Sync Garmin Data"** button in the upper right corner to sync latest training records in real-time
- No need to manually add or manage data

**Keep User Backend** (Full CRUD):

<div align="center">
<img src="static/image/keepDataMonitor.png" alt="Keep Data Backend" width="80%">
<p><i>Keep Data Backend - Supports CRUD operations</i></p>
</div>

- Provides full CRUD functionality
- Due to Keep's closed ecosystem, manual data sync is needed (cannot frequently export Excel)
- Supports adding, editing, and deleting individual records

---

### 🛠️ Single Agent Debug Mode (Developer Option)

If you need to debug individual agents, you can use Streamlit debug interface:

```bash
# Start Query Agent (Theory Expert)
streamlit run SingleEngineApp/query_engine_streamlit_app.py --server.port 8503

# Start Media Agent (Logistics Intelligence)
streamlit run SingleEngineApp/media_engine_streamlit_app.py --server.port 8502

# Start Insight Agent (Data Analyst)
streamlit run SingleEngineApp/insight_engine_streamlit_app.py --server.port 8501
```

---

## 📂 Project Structure

```
Synapse_Run/
├── QueryEngine/                   # Theory Expert Agent
│   ├── agent.py                   # Agent main logic
│   ├── llms/base.py               # LLM interface wrapper
│   ├── nodes/                     # Processing nodes (search/summary/formatting)
│   ├── tools/                     # Tavily search tools
│   ├── prompts/prompts.py         # Prompt templates
│   ├── state/state.py             # State management
│   └── utils/config.py            # Configuration management
│
├── MediaEngine/                   # Logistics Intelligence Agent
│   ├── agent.py                   # Agent main logic
│   ├── llms/base.py               # LLM interface
│   ├── nodes/                     # Processing nodes
│   ├── tools/                     # Bocha search tools
│   ├── prompts/prompts.py         # Prompt templates
│   ├── state/state.py             # State management
│   └── utils/config.py            # Configuration management
│
├── InsightEngine/                 # Data Analyst Agent
│   ├── agent.py                   # Agent main logic
│   ├── llms/base.py               # LLM interface wrapper
│   ├── nodes/                     # Processing nodes
│   ├── tools/                     # Database query tools (Keep/Garmin)
│   ├── prompts/                   # Prompt templates & tool descriptions
│   ├── state/state.py             # State management
│   └── utils/config.py            # Configuration management
│
├── ReportEngine/                  # Report Generator Agent
│   ├── agent.py                   # Agent main logic
│   ├── llms/base.py               # LLM interface
│   ├── nodes/                     # Report generation nodes
│   ├── report_template/           # 20+ professional report templates
│   │   ├── Training Theory Comparison Template.md
│   │   ├── Nutrition Strategy Template.md
│   │   ├── Injury Recovery Template.md
│   │   └── ... (20+ professional templates)
│   ├── prompts/prompts.py         # Prompt templates
│   ├── state/state.py             # State management
│   └── utils/config.py            # Configuration management
│
├── ForumEngine/                   # Forum Engine
│   ├── monitor.py                 # Log monitoring and forum management
│   └── llm_host.py                # LLM host module
│
├── routes/                        # Flask routing module
│   ├── routes/                    # Sub-routes directory
│   ├── utils/                     # Route utility functions
│   ├── setup.py                   # Setup page routes
│   └── training_data.py           # Training data management routes
│
├── SingleEngineApp/               # Single Agent debug interface
│   ├── query_engine_streamlit_app.py    # Query Agent debug
│   ├── media_engine_streamlit_app.py    # Media Agent debug
│   └── insight_engine_streamlit_app.py  # Insight Agent debug
│
├── scripts/                       # Utility scripts
│   ├── training_data_importer.py  # Training data importer
│   ├── training_tables.sql        # Database table structure
│   └── clear_reports.sh           # Clear reports script
│
├── templates/                     # Flask frontend templates
│   ├── index.html                 # Main interface
│   ├── setup.html                 # Configuration page
│   ├── training_data.html         # Keep data backend
│   └── training_data_garmin.html  # Garmin data backend
│
├── static/                        # Static resources
│   ├── image/                     # Image resources
│   │   ├── logo.png               # Project Logo
│   │   ├── finalResult.png        # Final report example
│   │   ├── forumResult.png        # Forum collaboration example
│   │   ├── healthCheck.png        # Health check interface
│   │   ├── apiSetting.png         # API configuration interface
│   │   ├── databaseSetting.png    # Database configuration interface
│   │   └── ... (more screenshots)
│   └── js/                        # JavaScript files
│
├── utils/                         # Common utility modules
│   ├── forum_reader.py            # Agent forum reading tool
│   ├── retry_helper.py            # Network request retry mechanism
│   ├── time_helper.py             # Time processing tool
│   ├── health_check.py            # System health check
│   └── config_reloader.py         # Configuration hot reload
│
├── logs/                          # Runtime log directory
│   └── forum.log                  # Forum communication log
│
├── reports/                       # Web-generated report files
├── final_reports/                 # Final report storage directory
├── *_streamlit_reports/           # Streamlit debug report directories
├── data/                          # Temporary data directory
├── docs/                          # Documentation directory
├── models/                        # Training record ORM models
│
├── app.py                         # Flask main application entry
├── config.py                      # Global configuration file
├── requirements.txt               # Python dependency list
├── README.md                      # Chinese documentation
├── README-EN.md                   # English documentation
└── .gitignore                     # Git ignore configuration
```

**Note**:
- Files in `logs/`, `reports/`, `data/` directories are not tracked by Git (configured in .gitignore)
- `*_streamlit_reports/` are temporary report directories generated by Streamlit debug mode

---

## ⚙️ Self-Adaptation Guide

### 1. Adjust MediaAgent Geographic Location Prompts

Edit `MediaEngine/prompts/prompts.py` and modify geographic location-related prompts according to your usual training locations:

```python
# Example: Change default location from "Haikou" to "Beijing"
LOCATION_PROMPT = """
You are a professional running logistics intelligence officer, primarily serving runners in the Beijing area.
When searching for weather, routes, races and other information, prioritize resources in Beijing and surrounding areas.
"""
```

### 2. Switch Data Source

The system supports both Keep and Garmin data sources, configurable in `config.py`:

```python
# Training data source configuration
TRAINING_DATA_SOURCE = "garmin"  # Options: "keep" or "garmin"
```

**Data Source Comparison**:

| Feature | Keep | Garmin |
|---------|------|--------|
| **Data Import** | Manual Excel upload | Auto-sync (email authorization) |
| **Data Update** | Manual addition | One-click sync |
| **Data Richness** | Basic training metrics | Advanced physiological metrics (HRV, training load, etc.) |
| **Backend Management** | Full CRUD | Read-only + sync button |

### 3. Customize Report Templates

Create your own Markdown templates in the `ReportEngine/report_template/` directory:

```markdown
# {title} - Custom Report Template

## Training Overview
{training_overview}

## Data Analysis
{data_analysis}

## Expert Advice
{expert_advice}

## Action Plan
{action_plan}
```

Template Variable Description:
- `{title}`: Report title
- `{training_overview}`: Training overview
- `{data_analysis}`: Data analysis results
- `{expert_advice}`: Expert advice
- `{action_plan}`: Action plan

---

## 🔌 API Usage Guide

### Importance of LLM Response Speed

**⚠️ Key Tip**: The forum collaboration mechanism is extremely sensitive to the response speed of each LLM!

**Problem**: If an agent's LLM responds too slowly, the forum's BrainStorm will become dominated by the fast-responding LLM, losing the advantage of multi-agent collaboration.

**Recommended Configuration**:

| Agent | Recommended Model | Reason |
|-------|------------------|--------|
| **Query Agent** | Qwen-Plus-Latest | High-speed reasoning, ensures fast search response |
| **Media Agent** | Qwen-Plus-Latest | High-speed reasoning, ensures fast intelligence gathering |
| **Insight Agent** | Qwen-Plus-Latest | High-speed reasoning, ensures fast data analysis |
| **Forum Host** | Qwen-Plus-Latest | High-speed reasoning, ensures fast forum coordination |
| **Report Agent** | Qwen3-Max / Kimi-K2 / GLM-4 | Can be slower, but needs strong coding ability to generate HTML reports |

**Principles**:
- Except for Report Agent, **uniformly use high-speed reasoning LLM** (Qwen series recommended)
- Ensure agents speak quickly to maintain forum activity
- Report Agent is not constrained by response speed and can use models with strong coding capabilities

### Supported LLM Providers

Any LLM compatible with OpenAI calling format can be used:

| Provider | Recommended Model | Application URL |
|----------|------------------|----------------|
| **Alibaba Cloud DashScope** | Qwen-Plus-Latest, Qwen3-Max | https://dashscope.aliyun.com/ |
| **Moonshot AI** | Kimi-K2 | https://platform.moonshot.cn/ |
| **Google Gemini** | Gemini-2.0-Flash-Exp | https://ai.google.dev/ |
| **Zhipu AI** | GLM-4, GLM-4-Plus | https://open.bigmodel.cn/ |
| **DeepSeek** | DeepSeek-Chat | https://platform.deepseek.com/ |

---

## 📸 Effect Demonstration

### Forum Collaboration Process

<div align="center">
<img src="static/image/forumResult.png" alt="Forum Collaboration Example" width="90%">
<p><i>Multiple agents brainstorm and collaborate through forum mechanism</i></p>
</div>

### Theory Expert Agent Work Example

<div align="center">
<img src="static/image/theoryExperResult.png" alt="Theory Expert Work Example" width="90%">
<p><i>Query Agent searches for running training theory and academic literature</i></p>
</div>

### Logistics Intelligence Agent Work Example

<div align="center">
<img src="static/image/logisticsIntelligenceResult.png" alt="Intelligence Officer Work Example" width="90%">
<p><i>Media Agent collects practical intelligence on races, weather, equipment, etc.</i></p>
</div>

### Data Analyst Agent Work Example

<div align="center">
<img src="static/image/sportScientistResult.png" alt="Data Analysis Example" width="90%">
<p><i>Insight Agent deeply mines historical training data</i></p>
</div>

### Final Intelligent Report

<div align="center">
<img src="static/image/finalResult.png" alt="Final Report Example" width="90%">
<p><i>Professional training analysis report generated by Report Agent</i></p>
</div>

---

## 🔧 Extension Suggestions

### InsightAgent Data Source Extension

**✅ Supported Data Sources**: Keep, Garmin Connect

**🚀 Extendable Data Sources**:

The system adopts modular design, making it easy to integrate data from more sports platforms:

| Data Source | Integration Difficulty | API Support | Recommendation |
|------------|----------------------|------------|----------------|
| **Strava** | ⭐⭐ | Official API well-developed | ⭐⭐⭐⭐⭐ |
| **Nike Run Club** | ⭐⭐⭐⭐ | Requires reverse engineering | ⭐⭐⭐ |
| **Yuepao Circle** | ⭐⭐⭐ | Data export supported | ⭐⭐⭐ |
| **Codoon Sports** | ⭐⭐⭐ | Data export supported | ⭐⭐⭐ |
| **Apple Health** | ⭐⭐ | Exports XML format | ⭐⭐⭐⭐ |

**Extension Steps**:

1. **Data Source Adapter Development** (`InsightEngine/tools/`):
   ```python
   class StravaDataAdapter:
       def fetch_activities(self, access_token):
           # Call Strava API to fetch training data
           pass

       def convert_to_schema(self, strava_data):
           # Convert to system database schema
           pass
   ```

2. **Configuration File Update** (`config.py`):
   ```python
   TRAINING_DATA_SOURCE = "strava"  # New data source option
   STRAVA_CLIENT_ID = "your_client_id"
   STRAVA_CLIENT_SECRET = "your_client_secret"
   ```

3. **Backend Interface Extension** (`routes/training_data.py`):
   - Add Strava authorization button
   - Implement data sync interface

**Community Contributions Welcome**: If you successfully integrate new data sources, welcome to submit PR and share with the community!

---

## 🙏 Acknowledgments

The birth of this project is inseparable from the support of the open-source community. Special thanks to the **BettaFish(微舆)** project and its author [@666ghj](https://github.com/666ghj)!

**Why Pay Tribute to BettaFish?**

The BettaFish project demonstrated the powerful potential of multi-agent collaborative architecture in the field of public opinion analysis. Its innovative "forum-style" agent interaction mechanism, modular system design, and ultimate pursuit of code quality provided us with valuable reference examples. The engineering practice level and open-source spirit demonstrated by the author in the project are admirable!

**Synapse Run = BettaFish's Adaptation for Running Domain**

Based on the core architecture of BettaFish, we conducted deep customization for running training scenarios, hoping to bring this advanced multi-agent collaboration concept to more vertical fields, making AI truly become everyone's intelligent assistant.

**Thank you again for BettaFish's open-source contribution!** 🎉

---

## 📄 License

This project is open-sourced under the **GPL-2.0 License**.

This means:
- ✅ You can freely use, modify, and distribute this project
- ✅ You can use this project for commercial purposes
- ⚠️ If you distribute a modified version, it must also be open-sourced under the GPL-2.0 license
- ⚠️ You must retain the original copyright notice in modified code

For details, please refer to the [LICENSE](LICENSE) file.

---

## 📧 Contact

For any questions, suggestions, or collaboration intentions, feel free to contact us through the following methods:

- **📮 Email**: huangsuxiang5@gmail.com
- **💬 WeChat**: 13976457218
- **🐧 QQ**: 1736672988

**We look forward to communicating with you!** 💬

---

<div align="center">

### Let AI Become Your Intelligent Running Coach 🏃‍♂️

**Made with ❤️ by Synapse Run Team**

⭐ If this project helps you, please give us a Star! ⭐

</div>
