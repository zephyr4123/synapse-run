# -*- coding: utf-8 -*-
"""
SQLAlchemy数据库会话管理器
提供统一的数据库连接和会话管理
"""

import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
from typing import Optional
from contextlib import contextmanager

# 添加项目根目录到Python路径,以便导入config
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


class DatabaseSessionManager:
    """数据库会话管理器 - 单例模式"""

    _instance: Optional['DatabaseSessionManager'] = None
    _engine = None
    _session_factory = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化数据库连接"""
        if self._engine is None:
            self._initialize_engine()

    def _initialize_engine(self):
        """初始化SQLAlchemy引擎"""
        # 从config.py读取数据库配置
        try:
            import config
            db_host = getattr(config, 'DB_HOST', 'localhost')
            db_port = int(getattr(config, 'DB_PORT', 3306))
            db_user = getattr(config, 'DB_USER', '')
            db_password = getattr(config, 'DB_PASSWORD', '')
            db_name = getattr(config, 'DB_NAME', '')
            db_charset = getattr(config, 'DB_CHARSET', 'utf8mb4')
        except ImportError:
            # 如果无法导入config,尝试从环境变量读取(兼容性处理)
            db_host = os.getenv("DB_HOST", "localhost")
            db_port = int(os.getenv("DB_PORT", 3306))
            db_user = os.getenv("DB_USER", "")
            db_password = os.getenv("DB_PASSWORD", "")
            db_name = os.getenv("DB_NAME", "")
            db_charset = os.getenv("DB_CHARSET", "utf8mb4")

        # 验证配置完整性
        if not all([db_host, db_user, db_password, db_name]):
            raise ValueError(
                "数据库配置不完整! 请设置环境变量: DB_HOST, DB_USER, DB_PASSWORD, DB_NAME"
            )

        # 构建数据库连接URL
        database_url = (
            f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            f"?charset={db_charset}"
        )

        # 创建引擎
        self._engine = create_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,  # 自动检测连接是否有效
            pool_recycle=3600,   # 1小时回收连接
            echo=False,          # 不打印SQL语句
        )

        # 创建会话工厂
        self._session_factory = scoped_session(
            sessionmaker(
                bind=self._engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False
            )
        )

    @contextmanager
    def get_session(self):
        """
        获取数据库会话(上下文管理器)

        使用示例:
        ```python
        with db_manager.get_session() as session:
            results = session.query(Model).all()
        ```
        """
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_engine(self):
        """获取SQLAlchemy引擎"""
        return self._engine

    def close_all(self):
        """关闭所有连接"""
        if self._session_factory:
            self._session_factory.remove()
        if self._engine:
            self._engine.dispose()


# 全局单例实例
db_session_manager = DatabaseSessionManager()
