# -*- coding: utf-8 -*-
"""
训练数据搜索工具基类
定义所有数据源工具必须实现的接口
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class DBResponse:
    """封装工具的完整返回结果 - 通用响应格式"""
    tool_name: str
    parameters: Dict[str, Any]
    data_source: str  # 数据源标识: 'keep' 或 'garmin'
    results: List[Any] = None  # 数据记录列表 (KeepTrainingRecord 或 GarminTrainingRecord)
    results_count: int = 0
    statistics: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

    def __post_init__(self):
        if self.results is None:
            self.results = []
        self.results_count = len(self.results)


class BaseTrainingDataSearch(ABC):
    """
    训练数据搜索工具基类

    所有数据源的搜索工具必须继承此类并实现抽象方法
    提供统一的接口,但每个数据源使用各自的数据格式
    """

    def __init__(self, data_source: str):
        """
        初始化搜索工具

        Args:
            data_source: 数据源标识 ('keep' 或 'garmin')
        """
        self.data_source = data_source
        self.db_config = self._load_db_config()
        self._validate_config()

    @abstractmethod
    def _load_db_config(self) -> Dict[str, Any]:
        """
        加载数据库配置
        子类必须实现此方法从环境变量或配置文件读取配置

        Returns:
            数据库配置字典
        """
        pass

    @abstractmethod
    def _validate_config(self):
        """
        验证配置完整性
        子类必须实现此方法检查必需的配置项

        Raises:
            ValueError: 配置不完整时抛出异常
        """
        pass

    @abstractmethod
    def _execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """
        执行SQL查询

        Args:
            query: SQL查询语句
            params: 查询参数

        Returns:
            查询结果列表
        """
        pass

    # ===== 核心查询接口 (所有数据源必须实现) =====

    @abstractmethod
    def search_recent_trainings(
        self,
        days: int = 7,
        limit: int = 50
    ) -> DBResponse:
        """
        查询最近N天的训练记录

        Args:
            days: 查询最近多少天
            limit: 返回结果数量限制

        Returns:
            DBResponse对象
        """
        pass

    @abstractmethod
    def search_by_date_range(
        self,
        start_date: str,
        end_date: str,
        limit: int = 100
    ) -> DBResponse:
        """
        按日期范围查询训练记录

        Args:
            start_date: 开始日期 'YYYY-MM-DD'
            end_date: 结束日期 'YYYY-MM-DD'
            limit: 返回结果数量限制

        Returns:
            DBResponse对象
        """
        pass

    @abstractmethod
    def get_training_stats(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> DBResponse:
        """
        获取训练统计数据

        Args:
            start_date: 开始日期 'YYYY-MM-DD'
            end_date: 结束日期 'YYYY-MM-DD'

        Returns:
            DBResponse对象,statistics字段包含统计结果
        """
        pass

    @abstractmethod
    def search_by_distance_range(
        self,
        min_distance_km: float,
        max_distance_km: Optional[float] = None,
        limit: int = 50
    ) -> DBResponse:
        """
        按距离范围查询训练记录

        Args:
            min_distance_km: 最小距离(公里)
            max_distance_km: 最大距离(公里)
            limit: 返回结果数量限制

        Returns:
            DBResponse对象
        """
        pass

    @abstractmethod
    def search_by_heart_rate(
        self,
        min_avg_hr: int,
        max_avg_hr: Optional[int] = None,
        limit: int = 50
    ) -> DBResponse:
        """
        按心率区间查询训练记录

        Args:
            min_avg_hr: 最小平均心率
            max_avg_hr: 最大平均心率
            limit: 返回结果数量限制

        Returns:
            DBResponse对象
        """
        pass

    # ===== 工具辅助方法 =====

    def _calculate_pace(self, duration_seconds: int, distance_meters: Optional[float]) -> Optional[float]:
        """计算配速(秒/公里)"""
        if not distance_meters or distance_meters <= 0:
            return None
        distance_km = float(distance_meters) / 1000.0
        duration = float(duration_seconds)
        return duration / distance_km

    def get_supported_tools(self) -> List[str]:
        """
        获取当前数据源支持的工具列表

        Returns:
            工具名称列表
        """
        return [
            "search_recent_trainings",
            "search_by_date_range",
            "get_training_stats",
            "search_by_distance_range",
            "search_by_heart_rate"
        ]
