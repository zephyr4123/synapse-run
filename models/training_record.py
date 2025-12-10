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

# 延迟创建引擎的函数
def get_engine():
    """
    获取数据库引擎，每次调用都重新读取config配置
    这样可以确保在setup页面修改配置后能使用最新配置
    """
    return create_engine(
        f'mysql+pymysql://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}?charset={config.DB_CHARSET}',
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=False
    )

# 获取Session的函数
def get_session_local():
    """获取SessionLocal类，使用最新的engine配置"""
    engine = get_engine()
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)

# 为了兼容性，保留原来的变量名，但改为函数调用
engine = get_engine()
SessionLocal = get_session_local()


class TrainingRecordKeep(Base):
    """训练记录模型 - Keep数据源"""
    __tablename__ = 'training_records_keep'

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
    data_source = Column(String(64), default='keep_import')

    def __repr__(self):
        return f'<TrainingRecordKeep(id={self.id}, exercise_type={self.exercise_type}, start_time={self.start_time})>'

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


class TrainingRecordGarmin(Base):
    """训练记录模型 - Garmin数据源"""
    __tablename__ = 'training_records_garmin'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(64), default='default_user', index=True)

    # 基础训练信息
    activity_id = Column(String(128), nullable=True, index=True)
    activity_name = Column(String(255), nullable=True)
    sport_type = Column(String(64), nullable=False, index=True)
    start_time_gmt = Column(DateTime, nullable=False, index=True)
    end_time_gmt = Column(DateTime, nullable=False)
    duration_seconds = Column(Integer, nullable=False)
    distance_meters = Column(DECIMAL(10, 2), nullable=True)

    # 心率指标
    avg_heart_rate = Column(Integer, nullable=True)
    max_heart_rate = Column(Integer, nullable=True)
    hr_zone_1_seconds = Column(Integer, nullable=True)
    hr_zone_2_seconds = Column(Integer, nullable=True)
    hr_zone_3_seconds = Column(Integer, nullable=True)
    hr_zone_4_seconds = Column(Integer, nullable=True)
    hr_zone_5_seconds = Column(Integer, nullable=True)

    # 步频步幅指标
    avg_cadence = Column(Integer, nullable=True)
    max_cadence = Column(Integer, nullable=True)
    avg_stride_length_cm = Column(DECIMAL(10, 2), nullable=True)
    avg_vertical_oscillation_cm = Column(DECIMAL(10, 2), nullable=True)
    avg_ground_contact_time_ms = Column(Integer, nullable=True)
    vertical_ratio_percent = Column(DECIMAL(10, 2), nullable=True)
    total_steps = Column(Integer, nullable=True)

    # 功率指标
    avg_power_watts = Column(Integer, nullable=True)
    max_power_watts = Column(Integer, nullable=True)
    normalized_power_watts = Column(Integer, nullable=True)
    power_zone_1_seconds = Column(Integer, nullable=True)
    power_zone_2_seconds = Column(Integer, nullable=True)
    power_zone_3_seconds = Column(Integer, nullable=True)
    power_zone_4_seconds = Column(Integer, nullable=True)
    power_zone_5_seconds = Column(Integer, nullable=True)

    # 速度指标
    avg_speed_mps = Column(DECIMAL(10, 2), nullable=True)
    max_speed_mps = Column(DECIMAL(10, 2), nullable=True)

    # 训练效果指标
    aerobic_training_effect = Column(DECIMAL(4, 2), nullable=True)
    anaerobic_training_effect = Column(DECIMAL(4, 2), nullable=True)
    training_effect_label = Column(String(64), nullable=True)
    training_load = Column(Integer, nullable=True)

    # 卡路里和代谢指标
    activity_calories = Column(Integer, nullable=True)
    basal_metabolism_calories = Column(Integer, nullable=True)
    estimated_sweat_loss_ml = Column(Integer, nullable=True)

    # 强度时长
    moderate_intensity_minutes = Column(Integer, nullable=True)
    vigorous_intensity_minutes = Column(Integer, nullable=True)

    # 其他指标
    body_battery_change = Column(Integer, nullable=True)

    # 元数据
    add_ts = Column(BigInteger, nullable=False)
    last_modify_ts = Column(BigInteger, nullable=False)
    data_source = Column(String(64), default='garmin_import')

    def __repr__(self):
        return f'<TrainingRecordGarmin(id={self.id}, sport_type={self.sport_type}, start_time_gmt={self.start_time_gmt})>'

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'activity_id': self.activity_id,
            'activity_name': self.activity_name,
            'sport_type': self.sport_type,
            'start_time_gmt': self.start_time_gmt.strftime('%Y-%m-%d %H:%M:%S') if self.start_time_gmt else None,
            'end_time_gmt': self.end_time_gmt.strftime('%Y-%m-%d %H:%M:%S') if self.end_time_gmt else None,
            'duration_seconds': self.duration_seconds,
            'distance_meters': float(self.distance_meters) if self.distance_meters else None,
            'avg_heart_rate': self.avg_heart_rate,
            'max_heart_rate': self.max_heart_rate,
            'avg_cadence': self.avg_cadence,
            'avg_power_watts': self.avg_power_watts,
            'training_load': self.training_load,
            'add_ts': self.add_ts,
            'last_modify_ts': self.last_modify_ts,
            'data_source': self.data_source
        }


class TrainingRecordManager:
    """
    训练记录数据源管理器
    支持动态切换不同的数据源(Keep/Garmin)
    """

    # 数据源映射
    DATA_SOURCE_MAP = {
        'keep': TrainingRecordKeep,
        'garmin': TrainingRecordGarmin
    }

    # 字段映射（不同数据源的字段名可能不同）
    FIELD_MAPPING = {
        'keep': {
            'start_time': 'start_time',
            'end_time': 'end_time',
            'exercise_type': 'exercise_type'
        },
        'garmin': {
            'start_time': 'start_time_gmt',
            'end_time': 'end_time_gmt',
            'exercise_type': 'sport_type'
        }
    }

    def __init__(self, data_source: str = 'keep'):
        """
        初始化管理器

        Args:
            data_source: 数据源类型 ('keep' 或 'garmin')
        """
        if data_source not in self.DATA_SOURCE_MAP:
            raise ValueError(f"不支持的数据源: {data_source}. 请使用: {list(self.DATA_SOURCE_MAP.keys())}")

        self.data_source = data_source
        self.model_class = self.DATA_SOURCE_MAP[data_source]

    def get_model_class(self):
        """获取当前数据源的模型类"""
        return self.model_class

    def switch_source(self, data_source: str):
        """
        切换数据源

        Args:
            data_source: 新的数据源类型
        """
        if data_source not in self.DATA_SOURCE_MAP:
            raise ValueError(f"不支持的数据源: {data_source}")

        self.data_source = data_source
        self.model_class = self.DATA_SOURCE_MAP[data_source]

    def query(self, session):
        """
        创建查询对象

        Args:
            session: 数据库会话

        Returns:
            Query对象
        """
        return session.query(self.model_class)

    def create_record(self, **kwargs):
        """
        创建训练记录实例

        Args:
            **kwargs: 记录字段参数

        Returns:
            训练记录实例
        """
        return self.model_class(**kwargs)

    def get_field(self, field_name: str):
        """
        获取当前数据源的实际字段名或字段对象

        Args:
            field_name: 通用字段名 ('start_time', 'end_time', 'exercise_type')

        Returns:
            实际的模型字段对象
        """
        actual_field_name = self.FIELD_MAPPING[self.data_source].get(field_name, field_name)
        return getattr(self.model_class, actual_field_name)


def get_db_session():
    """获取数据库会话"""
    session = SessionLocal()
    try:
        return session
    except Exception as e:
        session.close()
        raise e
