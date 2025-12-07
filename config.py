# -*- coding: utf-8 -*-
"""
Synapse Run 配置文件
请在使用前填写您自己的API密钥和数据库配置信息
"""

# ============================== 数据库配置 ==============================
# MySQL数据库连接配置
# 请根据您的实际MySQL配置修改以下参数
DB_HOST = "localhost"           # 数据库主机地址,如 "localhost" 或 "127.0.0.1"
DB_PORT = 3306                  # 数据库端口,默认3306
DB_USER = "your_db_username"    # 数据库用户名
DB_PASSWORD = "your_db_password"  # 数据库密码
DB_NAME = "traningData"         # 数据库名称(建议保持此名称)
DB_CHARSET = "utf8mb4"          # 字符集,建议使用utf8mb4


# ============================== LLM配置 ==============================
# 所有Agent都需要配置兼容OpenAI格式的LLM API
# 必需参数: API_KEY, BASE_URL, MODEL_NAME
#
# 重要说明:
# 1. 论坛协作机制对LLM响应速度敏感,建议除Report Agent外统一使用高速推理模型
# 2. 推荐使用Qwen系列API,确保响应速度一致性
# 3. Report Agent可使用编码能力强的模型(如Qwen3-Max、Kimi-K2、GLM-4等)

# Insight Agent - 数据分析师Agent
# 推荐: Qwen-Plus-Latest (高速推理,适合数据分析)
# 申请地址: https://dashscope.aliyun.com/
INSIGHT_ENGINE_API_KEY = "your_qwen_api_key_here"
INSIGHT_ENGINE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
INSIGHT_ENGINE_MODEL_NAME = "qwen-plus-latest"

# Media Agent - 后勤情报官Agent
# 推荐: Qwen-Plus-Latest (高速推理,适合信息检索)
# 申请地址: https://dashscope.aliyun.com/
MEDIA_ENGINE_API_KEY = "your_qwen_api_key_here"
MEDIA_ENGINE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MEDIA_ENGINE_MODEL_NAME = "qwen-plus-latest"

# Query Agent - 理论专家Agent
# 推荐: Qwen-Plus-Latest (高速推理,适合知识检索)
# 申请地址: https://dashscope.aliyun.com/
QUERY_ENGINE_API_KEY = "your_qwen_api_key_here"
QUERY_ENGINE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
QUERY_ENGINE_MODEL_NAME = "qwen-plus-latest"

# Report Agent - 报告生成器Agent
# 推荐: Qwen3-Max (强编码能力,适合生成HTML报告)
# 可选: Kimi-K2, GLM-4, GLM-4-Plus等
# 申请地址: https://dashscope.aliyun.com/
REPORT_ENGINE_API_KEY = "your_qwen_api_key_here"
REPORT_ENGINE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
REPORT_ENGINE_MODEL_NAME = "qwen3-max"

# Forum Host - 论坛主持人LLM
# 推荐: Qwen-Plus-Latest (高速推理,保证论坛协调迅速)
# 申请地址: https://dashscope.aliyun.com/
FORUM_HOST_API_KEY = "your_qwen_api_key_here"
FORUM_HOST_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
FORUM_HOST_MODEL_NAME = "qwen-plus-latest"


# ============================== 网络工具配置 ==============================
# 网络搜索工具API密钥配置

# Tavily Search API - 用于Query Agent的专业知识搜索
# 申请地址: https://www.tavily.com/
TAVILY_API_KEY = "your_tavily_api_key_here"

# Bocha Web Search API - 用于Media Agent的实用信息检索
# 申请地址: https://open.bochaai.com/
BOCHA_WEB_SEARCH_API_KEY = "your_bocha_api_key_here"
