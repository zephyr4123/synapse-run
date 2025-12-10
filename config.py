# -*- coding: utf-8 -*-
"""
Synapse Run 配置文件
请在使用前填写您自己的API密钥和数据库配置信息
"""

# ============================== 数据库配置 ==============================
# MySQL数据库连接配置
# 请根据您的实际MySQL配置修改以下参数
DB_HOST = "localhost" # 数据库主机地址,如 "localhost" 或 "127.0.0.1"
DB_PORT = 3306 # 数据库端口,默认3306
DB_USER = "" # 数据库用户名
DB_PASSWORD = "" # 数据库密码
DB_NAME = "traningDate" # 数据库名称(建议保持此名称)
DB_CHARSET = "utf8mb4"          # 字符集,建议使用utf8mb4

# 训练数据源配置
# 支持的数据源: 'keep' (Keep运动APP) 或 'garmin' (Garmin设备)
TRAINING_DATA_SOURCE = "garmin"

# Garmin账户配置(仅当TRAINING_DATA_SOURCE为garmin时需要)
GARMIN_EMAIL = ""
GARMIN_PASSWORD = ""
GARMIN_IS_CN = True  # True: 中国区账户, False: 国际区账户


# ============================== LLM配置 ==============================
# 统一LLM配置 - 所有Agent共享相同的API Key和Base URL
# 必需参数: LLM_API_KEY, LLM_BASE_URL
#
# 模型配置说明:
# 1. DEFAULT_MODEL_NAME: 默认模型,用于InsightEngine/MediaEngine/QueryEngine/ForumHost
# 2. REPORT_MODEL_NAME: 报告生成专用模型,用于ReportEngine
#
# 推荐配置:
# - DEFAULT_MODEL_NAME: qwen-plus-latest (高速推理,适合数据分析/检索/协作)
# - REPORT_MODEL_NAME: qwen3-max (强编码能力,适合生成HTML报告)
#
# 申请地址: https://dashscope.aliyun.com/

# 统一API配置
LLM_API_KEY = ""
LLM_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# 模型配置
DEFAULT_MODEL_NAME = "qwen-plus-latest" # 用于: InsightEngine, MediaEngine, QueryEngine, ForumHost
REPORT_MODEL_NAME = "qwen3-max" # 用于: ReportEngine


# ============================== 网络工具配置 ==============================
# 网络搜索工具API密钥配置

# Tavily Search API - 用于Query Agent的专业知识搜索
# 申请地址: https://www.tavily.com/
TAVILY_API_KEY = ""

# Bocha Web Search API - 用于Media Agent的实用信息检索
# 申请地址: https://open.bochaai.com/
BOCHA_WEB_SEARCH_API_KEY = ""
