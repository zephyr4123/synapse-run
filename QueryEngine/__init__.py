"""
Theory Expert Agent (理论专家Agent)
中长跑运动科学理论专家 - 基于LangGraph的AI代理实现
"""

from .agent import TheoryExpertAgent, create_agent
from .utils.config import Config, load_config

__version__ = "2.0.0"
__author__ = "MultiRunningAgents Team"

__all__ = ["TheoryExpertAgent", "create_agent", "Config", "load_config"]
