# -*- coding: utf-8 -*-
"""
统一配置热重载工具
用于在运行时动态重载config.py配置，支持配置页面修改后即时生效

包含config.py中的所有20个配置项:
- 数据库配置(6项): DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, DB_CHARSET
- 训练数据源配置(4项): TRAINING_DATA_SOURCE, GARMIN_EMAIL, GARMIN_PASSWORD, GARMIN_IS_CN
- LLM配置(4项): LLM_API_KEY, LLM_BASE_URL, DEFAULT_MODEL_NAME, REPORT_MODEL_NAME
- 网络工具配置(2项): TAVILY_API_KEY, BOCHA_WEB_SEARCH_API_KEY
"""

import importlib
import sys
import os
from typing import Optional, Dict, Any, Tuple
from threading import Lock
from dataclasses import dataclass
from pathlib import Path

# 确保项目根目录在Python路径中
root_dir = Path(__file__).parent.parent.absolute()
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))


@dataclass
class ConfigSnapshot:
    """配置快照 - 包含config.py中的所有配置项"""

    # 数据库配置
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_CHARSET: str

    # 训练数据源配置
    TRAINING_DATA_SOURCE: str
    GARMIN_EMAIL: str
    GARMIN_PASSWORD: str
    GARMIN_IS_CN: bool

    # LLM配置
    LLM_API_KEY: str
    LLM_BASE_URL: str
    DEFAULT_MODEL_NAME: str
    REPORT_MODEL_NAME: str

    # 网络工具配置
    TAVILY_API_KEY: str
    BOCHA_WEB_SEARCH_API_KEY: str

    @classmethod
    def from_module(cls, config_module) -> 'ConfigSnapshot':
        """从config模块创建快照"""
        return cls(
            # 数据库配置
            DB_HOST=getattr(config_module, 'DB_HOST', 'localhost'),
            DB_PORT=getattr(config_module, 'DB_PORT', 3306),
            DB_USER=getattr(config_module, 'DB_USER', ''),
            DB_PASSWORD=getattr(config_module, 'DB_PASSWORD', ''),
            DB_NAME=getattr(config_module, 'DB_NAME', ''),
            DB_CHARSET=getattr(config_module, 'DB_CHARSET', 'utf8mb4'),

            # 训练数据源配置
            TRAINING_DATA_SOURCE=getattr(config_module, 'TRAINING_DATA_SOURCE', 'keep'),
            GARMIN_EMAIL=getattr(config_module, 'GARMIN_EMAIL', ''),
            GARMIN_PASSWORD=getattr(config_module, 'GARMIN_PASSWORD', ''),
            GARMIN_IS_CN=getattr(config_module, 'GARMIN_IS_CN', True),

            # LLM配置
            LLM_API_KEY=getattr(config_module, 'LLM_API_KEY', ''),
            LLM_BASE_URL=getattr(config_module, 'LLM_BASE_URL', ''),
            DEFAULT_MODEL_NAME=getattr(config_module, 'DEFAULT_MODEL_NAME', 'qwen-plus-latest'),
            REPORT_MODEL_NAME=getattr(config_module, 'REPORT_MODEL_NAME', 'qwen3-max'),

            # 网络工具配置
            TAVILY_API_KEY=getattr(config_module, 'TAVILY_API_KEY', ''),
            BOCHA_WEB_SEARCH_API_KEY=getattr(config_module, 'BOCHA_WEB_SEARCH_API_KEY', ''),
        )

    def get_changes(self, other: 'ConfigSnapshot') -> Dict[str, Tuple[Any, Any]]:
        """
        对比两个配置快照，返回变化的配置项

        Returns:
            {配置项名称: (旧值, 新值)}
        """
        changes = {}
        for field in self.__dataclass_fields__:
            old_value = getattr(self, field)
            new_value = getattr(other, field)
            if old_value != new_value:
                # 隐藏敏感信息
                if 'PASSWORD' in field or 'API_KEY' in field:
                    old_display = f"{old_value[:10]}..." if len(old_value) > 10 else old_value
                    new_display = f"{new_value[:10]}..." if len(new_value) > 10 else new_value
                    changes[field] = (old_display, new_display)
                else:
                    changes[field] = (old_value, new_value)
        return changes


class ConfigReloader:
    """
    配置热重载管理器

    特性:
    1. 线程安全的单例模式
    2. 自动检测config.py变化
    3. 支持变化追踪和日志记录
    4. 包含config.py中的所有20个配置项
    """

    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._config_module = None
            self._reload_count = 0
            self._last_snapshot: Optional[ConfigSnapshot] = None

    def reload_config(self, verbose: bool = True) -> bool:
        """
        重载config.py配置文件

        Args:
            verbose: 是否打印重载日志

        Returns:
            是否重载成功
        """
        try:
            # 保存旧快照
            old_snapshot = self._last_snapshot

            # 检查config模块是否已导入
            if 'config' in sys.modules:
                # 重新加载config模块
                import config as root_config
                importlib.reload(root_config)
                self._config_module = root_config
                self._reload_count += 1

                # 创建新快照
                new_snapshot = ConfigSnapshot.from_module(root_config)
                self._last_snapshot = new_snapshot

                if verbose:
                    print(f"🔄 配置热重载成功 (第{self._reload_count}次)")

                    # 显示关键配置
                    print(f"   数据源: {new_snapshot.TRAINING_DATA_SOURCE.upper()}")
                    print(f"   数据库: {new_snapshot.DB_HOST}:{new_snapshot.DB_PORT}/{new_snapshot.DB_NAME}")
                    print(f"   LLM模型: 默认={new_snapshot.DEFAULT_MODEL_NAME}, 报告={new_snapshot.REPORT_MODEL_NAME}")

                    # 显示变化
                    if old_snapshot:
                        changes = old_snapshot.get_changes(new_snapshot)
                        if changes:
                            print(f"   📝 检测到 {len(changes)} 项配置变化:")
                            for key, (old_val, new_val) in changes.items():
                                print(f"      - {key}: {old_val} → {new_val}")

                return True
            else:
                # 首次导入config
                import config as root_config
                self._config_module = root_config
                self._last_snapshot = ConfigSnapshot.from_module(root_config)

                if verbose:
                    print("✅ 配置模块首次加载")
                    print(f"   数据源: {self._last_snapshot.TRAINING_DATA_SOURCE.upper()}")
                    print(f"   数据库: {self._last_snapshot.DB_HOST}:{self._last_snapshot.DB_PORT}/{self._last_snapshot.DB_NAME}")

                return True

        except Exception as e:
            if verbose:
                print(f"❌ 配置重载失败: {str(e)}")
            return False

    def get_config_snapshot(self) -> Optional[ConfigSnapshot]:
        """
        获取当前配置快照(自动重载最新配置)

        Returns:
            配置快照对象
        """
        self.reload_config(verbose=False)
        return self._last_snapshot

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """
        获取配置值(自动重载最新配置)

        Args:
            key: 配置项名称(必须是config.py中的20个配置项之一)
            default: 默认值

        Returns:
            配置值
        """
        snapshot = self.get_config_snapshot()
        if snapshot and hasattr(snapshot, key):
            return getattr(snapshot, key)
        return default

    def get_all_config(self) -> Dict[str, Any]:
        """
        获取所有配置项(自动重载最新配置)

        Returns:
            配置字典(包含20个配置项)
        """
        snapshot = self.get_config_snapshot()
        if snapshot:
            return {
                field: getattr(snapshot, field)
                for field in snapshot.__dataclass_fields__
            }
        return {}


# 全局单例
_config_reloader = ConfigReloader()


def reload_config(verbose: bool = True) -> bool:
    """
    便捷函数: 重载配置

    Args:
        verbose: 是否打印重载日志

    Returns:
        是否重载成功
    """
    return _config_reloader.reload_config(verbose)


def get_config_snapshot() -> Optional[ConfigSnapshot]:
    """
    便捷函数: 获取配置快照(自动重载)

    Returns:
        配置快照对象
    """
    return _config_reloader.get_config_snapshot()


def get_config_value(key: str, default: Any = None) -> Any:
    """
    便捷函数: 获取配置值(自动重载)

    Args:
        key: 配置项名称(必须是以下20个之一):
            - DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, DB_CHARSET
            - TRAINING_DATA_SOURCE, GARMIN_EMAIL, GARMIN_PASSWORD, GARMIN_IS_CN
            - LLM_API_KEY, LLM_BASE_URL, DEFAULT_MODEL_NAME, REPORT_MODEL_NAME
            - TAVILY_API_KEY, BOCHA_WEB_SEARCH_API_KEY
        default: 默认值

    Returns:
        配置值
    """
    return _config_reloader.get_config_value(key, default)


def get_all_config() -> Dict[str, Any]:
    """
    便捷函数: 获取所有配置(自动重载)

    Returns:
        配置字典(包含20个配置项)
    """
    return _config_reloader.get_all_config()


if __name__ == '__main__':
    # 测试代码
    print("=" * 80)
    print("配置热重载工具测试")
    print("=" * 80)

    # 首次加载
    reload_config()

    # 获取配置快照
    snapshot = get_config_snapshot()
    if snapshot:
        print("\n📊 配置快照内容:")
        print(f"   数据库: {snapshot.DB_HOST}:{snapshot.DB_PORT}/{snapshot.DB_NAME}")
        print(f"   数据源: {snapshot.TRAINING_DATA_SOURCE}")
        print(f"   LLM: {snapshot.LLM_BASE_URL}")
        print(f"   模型: {snapshot.DEFAULT_MODEL_NAME}")

    # 获取单个配置值
    print(f"\n📝 单个配置项测试:")
    print(f"   TRAINING_DATA_SOURCE: {get_config_value('TRAINING_DATA_SOURCE')}")
    print(f"   DB_NAME: {get_config_value('DB_NAME')}")
    print(f"   DEFAULT_MODEL_NAME: {get_config_value('DEFAULT_MODEL_NAME')}")

    # 获取所有配置
    all_config = get_all_config()
    print(f"\n📦 配置项总数: {len(all_config)}/20")

    # 模拟配置变化检测
    print("\n" + "=" * 80)
    print("提示: 修改config.py后再次运行此脚本可查看变化检测效果")
    print("=" * 80)
