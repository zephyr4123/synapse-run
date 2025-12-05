# -*- coding: utf-8 -*-
"""
训练记录ORM模型
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, BigInteger, Text
from sqlalchemy.dialects.mysql import DECIMAL, LONGTEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json
import config

# 创建基类
Base = declarative_base()

# 创建数据库引擎
engine = create_engine(
    f'mysql+pymysql://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}?charset={config.DB_CHARSET}',
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)

# 创建Session类
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class TrainingRecord(Base):
    """训练记录模型"""
    __tablename__ = 'training_records'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(64), default='default_user', index=True)
    exercise_type = Column(String(32), nullable=False, index=True)
    duration_seconds = Column(Integer, nullable=False)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)
    calories = Column(Integer, nullable=True)
    distance_meters = Column(DECIMAL(10, 2), nullable=True)
    avg_heart_rate = Column(Integer, nullable=True)
    max_heart_rate = Column(Integer, nullable=True)
    heart_rate_data = Column(LONGTEXT, nullable=True)
    add_ts = Column(BigInteger, nullable=False)
    last_modify_ts = Column(BigInteger, nullable=False)
    data_source = Column(String(64), default='manual_import')

    def __repr__(self):
        return f'<TrainingRecord(id={self.id}, exercise_type={self.exercise_type}, start_time={self.start_time})>'

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'exercise_type': self.exercise_type,
            'duration_seconds': self.duration_seconds,
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S') if self.start_time else None,
            'end_time': self.end_time.strftime('%Y-%m-%d %H:%M:%S') if self.end_time else None,
            'calories': self.calories,
            'distance_meters': float(self.distance_meters) if self.distance_meters else None,
            'avg_heart_rate': self.avg_heart_rate,
            'max_heart_rate': self.max_heart_rate,
            'heart_rate_data': self.heart_rate_data,
            'add_ts': self.add_ts,
            'last_modify_ts': self.last_modify_ts,
            'data_source': self.data_source
        }


def get_db_session():
    """获取数据库会话"""
    session = SessionLocal()
    try:
        return session
    except Exception as e:
        session.close()
        raise e
