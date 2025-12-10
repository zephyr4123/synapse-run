# -*- coding: utf-8 -*-
"""
训练数据库ORM模型定义
使用SQLAlchemy定义training_records_keep和training_records_garmin表结构
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, BigInteger, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class TrainingRecordKeep(Base):
    """Keep训练记录表ORM模型"""
    __tablename__ = 'training_records_keep'

    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 用户标识
    user_id = Column(String(255), nullable=False, default='default_user', index=True)

    # 基础训练信息
    exercise_type = Column(String(100), nullable=False, index=True)
    duration_seconds = Column(Integer, nullable=False)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)

    # 运动指标
    calories = Column(Integer, nullable=True)
    distance_meters = Column(Float, nullable=True)
    avg_heart_rate = Column(Integer, nullable=True, index=True)
    max_heart_rate = Column(Integer, nullable=True)

    # 详细数据(JSON格式)
    heart_rate_data = Column(Text, nullable=True)

    # 元数据
    add_ts = Column(BigInteger, nullable=False)
    last_modify_ts = Column(BigInteger, nullable=False)
    data_source = Column(String(100), nullable=False, default='keep_import')

    def __repr__(self):
        return f"<KeepTraining(id={self.id}, type={self.exercise_type}, time={self.start_time})>"


class TrainingRecordGarmin(Base):
    """Garmin训练记录表ORM模型"""
    __tablename__ = 'training_records_garmin'

    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 用户标识
    user_id = Column(String(255), nullable=False, default='default_user', index=True)

    # 基础训练信息
    activity_id = Column(String(100), nullable=True, unique=True, index=True)
    activity_name = Column(String(255), nullable=True)
    sport_type = Column(String(100), nullable=False, index=True)
    start_time_gmt = Column(DateTime, nullable=False, index=True)
    end_time_gmt = Column(DateTime, nullable=False)
    duration_seconds = Column(Integer, nullable=False)
    distance_meters = Column(Float, nullable=True, index=True)

    # 心率指标
    avg_heart_rate = Column(Integer, nullable=True, index=True)
    max_heart_rate = Column(Integer, nullable=True)
    hr_zone_1_seconds = Column(Integer, nullable=True)
    hr_zone_2_seconds = Column(Integer, nullable=True)
    hr_zone_3_seconds = Column(Integer, nullable=True)
    hr_zone_4_seconds = Column(Integer, nullable=True)
    hr_zone_5_seconds = Column(Integer, nullable=True)

    # 步频步幅指标
    avg_cadence = Column(Integer, nullable=True)
    max_cadence = Column(Integer, nullable=True)
    avg_stride_length_cm = Column(Float, nullable=True)
    avg_vertical_oscillation_cm = Column(Float, nullable=True)
    avg_ground_contact_time_ms = Column(Integer, nullable=True)
    vertical_ratio_percent = Column(Float, nullable=True)
    total_steps = Column(Integer, nullable=True)

    # 功率指标
    avg_power_watts = Column(Integer, nullable=True, index=True)
    max_power_watts = Column(Integer, nullable=True)
    normalized_power_watts = Column(Integer, nullable=True)
    power_zone_1_seconds = Column(Integer, nullable=True)
    power_zone_2_seconds = Column(Integer, nullable=True)
    power_zone_3_seconds = Column(Integer, nullable=True)
    power_zone_4_seconds = Column(Integer, nullable=True)
    power_zone_5_seconds = Column(Integer, nullable=True)

    # 速度指标
    avg_speed_mps = Column(Float, nullable=True)
    max_speed_mps = Column(Float, nullable=True)

    # 训练效果指标
    aerobic_training_effect = Column(Float, nullable=True)
    anaerobic_training_effect = Column(Float, nullable=True)
    training_effect_label = Column(String(100), nullable=True)
    training_load = Column(Integer, nullable=True, index=True)

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
    data_source = Column(String(100), nullable=False, default='garmin_import')

    def __repr__(self):
        return f"<GarminTraining(id={self.id}, type={self.sport_type}, time={self.start_time_gmt})>"
