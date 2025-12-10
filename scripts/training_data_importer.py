# -*- coding: utf-8 -*-
"""
统一训练数据导入模块
支持Keep Excel文件和Garmin Connect在线数据导入
"""

import sys
from pathlib import Path
from datetime import datetime
import time
import pandas as pd

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 重要: 先导入config,确保数据库配置在创建engine前加载
import config

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from garminconnect import Garmin
from models.training_record import TrainingRecordKeep, TrainingRecordGarmin, Base, TrainingRecordManager, get_session_local


class BaseImporter:
    """训练数据导入器基类"""

    def __init__(self, db_engine=None):
        """
        初始化导入器

        Args:
            db_engine: SQLAlchemy引擎,如果为None则直接从config构建
        """
        if db_engine:
            self.engine = db_engine
        else:
            # 直接从config构建引擎,避免importlib.reload的不确定性
            connection_string = (
                f'mysql+pymysql://{config.DB_USER}:{config.DB_PASSWORD}'
                f'@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}'
                f'?charset={config.DB_CHARSET}'
            )
            self.engine = create_engine(
                connection_string,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False
            )

    def create_table_if_not_exists(self):
        """如果表不存在则创建"""
        Base.metadata.create_all(bind=self.engine)


class KeepDataImporter(BaseImporter):
    """Keep数据导入器 - 从Excel文件导入"""

    BATCH_SIZE = 100  # 批量提交大小

    def __init__(self, data_file: str, db_engine=None):
        """
        初始化Keep导入器

        Args:
            data_file: Excel数据文件路径
            db_engine: SQLAlchemy引擎
        """
        super().__init__(db_engine)
        self.data_file = data_file
        self.SessionLocal = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)

    def load_data(self) -> pd.DataFrame:
        """加载Excel数据文件"""
        if not Path(self.data_file).exists():
            raise FileNotFoundError(f"数据文件不存在: {self.data_file}")

        # 根据文件扩展名选择加载方式
        file_ext = Path(self.data_file).suffix.lower()
        if file_ext in ['.xlsx', '.xls']:
            df = pd.read_excel(self.data_file)
        elif file_ext == '.csv':
            df = pd.read_csv(self.data_file)
        else:
            raise ValueError(f"不支持的文件格式: {file_ext}")

        # 删除运动轨迹列
        if '运动轨迹' in df.columns:
            df = df.drop(columns=['运动轨迹'])

        return df

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """数据清洗"""
        # 填充空值
        df = df.fillna({
            '运动时长(秒)': 0,
            '卡路里': 0,
            '运动距离(米)': 0.0,
            '平均心率': 0,
            '最大心率': 0,
            '心率记录': '[]'
        })

        # 转换数据类型
        df['运动时长(秒)'] = df['运动时长(秒)'].astype(int)
        df['卡路里'] = df['卡路里'].astype(int)
        df['运动距离(米)'] = df['运动距离(米)'].astype(float)
        df['平均心率'] = df['平均心率'].astype(int)
        df['最大心率'] = df['最大心率'].astype(int)

        # 时间格式统一
        df['开始时间'] = pd.to_datetime(df['开始时间'])
        df['结束时间'] = pd.to_datetime(df['结束时间'])

        return df

    def import_to_database(self, df: pd.DataFrame, truncate_first: bool = False) -> dict:
        """
        导入数据到数据库

        Args:
            df: 待导入的DataFrame
            truncate_first: 是否先清空表

        Returns:
            dict: 导入结果统计 {'success': int, 'failed': int, 'total': int}
        """
        # 创建表(如果不存在)
        self.create_table_if_not_exists()

        session = self.SessionLocal()
        try:
            # 覆盖写入模式:先清空表
            if truncate_first:
                session.query(TrainingRecordKeep).delete()
                session.commit()

            now_ts = int(datetime.now().timestamp())
            success_count = 0
            failed_count = 0
            batch_records = []

            for idx, row in df.iterrows():
                try:
                    record = TrainingRecordKeep(
                        user_id='default_user',
                        exercise_type=row['运动类型'],
                        duration_seconds=int(row['运动时长(秒)']),
                        start_time=row['开始时间'].to_pydatetime(),
                        end_time=row['结束时间'].to_pydatetime(),
                        calories=int(row['卡路里']) if pd.notna(row['卡路里']) else None,
                        distance_meters=float(row['运动距离(米)']) if pd.notna(row['运动距离(米)']) else None,
                        avg_heart_rate=int(row['平均心率']) if pd.notna(row['平均心率']) else None,
                        max_heart_rate=int(row['最大心率']) if pd.notna(row['最大心率']) else None,
                        heart_rate_data=str(row['心率记录']) if pd.notna(row['心率记录']) else '[]',
                        add_ts=now_ts,
                        last_modify_ts=now_ts,
                        data_source='keep_import'
                    )

                    batch_records.append(record)
                    success_count += 1

                    # 批量提交
                    if len(batch_records) >= self.BATCH_SIZE:
                        session.bulk_save_objects(batch_records)
                        session.commit()
                        batch_records = []

                except Exception as e:
                    failed_count += 1
                    session.rollback()

            # 提交剩余记录
            if batch_records:
                session.bulk_save_objects(batch_records)
                session.commit()

            return {
                'success': success_count,
                'failed': failed_count,
                'total': len(df)
            }

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def run(self, truncate_first: bool = False) -> dict:
        """
        执行完整导入流程

        Args:
            truncate_first: 是否覆盖写入

        Returns:
            dict: 导入结果统计
        """
        try:
            # 加载数据
            df = self.load_data()

            # 清洗数据
            df = self.clean_data(df)

            # 导入数据库
            result = self.import_to_database(df, truncate_first=truncate_first)

            return result

        except Exception as e:
            raise e


class GarminDataImporter(BaseImporter):
    """Garmin数据导入器 - 从Garmin Connect在线抓取"""

    BATCH_SIZE = 50  # 每次抓取数量
    MAX_COUNT = 1000  # 最多抓取数量

    def __init__(self, email: str, password: str, is_cn: bool = True, db_engine=None):
        """
        初始化Garmin导入器

        Args:
            email: Garmin账户邮箱
            password: Garmin账户密码
            is_cn: 是否为中国区账户
            db_engine: SQLAlchemy引擎
        """
        super().__init__(db_engine)
        self.email = email
        self.password = password
        self.is_cn = is_cn
        self.client = None

    def login(self) -> bool:
        """登录Garmin Connect"""
        try:
            self.client = Garmin(self.email, self.password, is_cn=self.is_cn)
            self.client.login()
            return True
        except Exception as e:
            raise Exception(f"Garmin登录失败: {e}")

    def fetch_activities(self) -> list:
        """
        抓取训练活动数据

        Returns:
            list: 过滤后的跑步活动列表
        """
        if not self.client:
            raise Exception("请先登录Garmin")

        all_activities = []
        start = 0

        while True:
            try:
                activities = self.client.get_activities(start, self.BATCH_SIZE)

                if not activities:
                    break

                count = len(activities)
                all_activities.extend(activities)

                # 翻页
                start += count

                # 安全退出机制
                if count < self.BATCH_SIZE:
                    break
                if start >= self.MAX_COUNT:
                    break

                # 防止请求过快
                time.sleep(1)

            except Exception as e:
                break

        # 过滤跑步数据
        running_activities = []
        for act in all_activities:
            act_type = act.get('activityType', {}).get('typeKey', '')
            if 'running' in act_type or 'treadmill' in act_type:
                running_activities.append(act)

        return running_activities

    def parse_activity(self, act: dict) -> dict:
        """
        解析单个活动数据为训练记录格式

        Args:
            act: Garmin活动数据

        Returns:
            dict: 训练记录数据,完全匹配SQL schema
        """
        # 基础训练信息
        activity_id = str(act.get('activityId', ''))
        activity_name = act.get('activityName', '未命名训练')
        sport_type = act.get('activityType', {}).get('typeKey', 'running')

        # 时间信息(GMT)
        start_time_str = act.get('startTimeGMT', '')
        end_time_str = act.get('endTimeGMT', '')

        try:
            # Garmin时间格式: "2024-01-20 08:30:00"
            start_time_gmt = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
            end_time_gmt = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')
        except:
            # 尝试其他格式
            try:
                start_time_gmt = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                end_time_gmt = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
            except:
                return None

        # 时长(秒)
        duration_seconds = int(act.get('duration', 0))

        # 距离(米)
        distance_meters = float(act.get('distance', 0)) if act.get('distance') else None

        # 心率指标
        avg_heart_rate = int(act.get('averageHR', 0)) if act.get('averageHR') else None
        max_heart_rate = int(act.get('maxHR', 0)) if act.get('maxHR') else None
        hr_zone_1_seconds = int(act.get('hrTimeInZone_1', 0)) if act.get('hrTimeInZone_1') else None
        hr_zone_2_seconds = int(act.get('hrTimeInZone_2', 0)) if act.get('hrTimeInZone_2') else None
        hr_zone_3_seconds = int(act.get('hrTimeInZone_3', 0)) if act.get('hrTimeInZone_3') else None
        hr_zone_4_seconds = int(act.get('hrTimeInZone_4', 0)) if act.get('hrTimeInZone_4') else None
        hr_zone_5_seconds = int(act.get('hrTimeInZone_5', 0)) if act.get('hrTimeInZone_5') else None

        # 步频步幅指标
        avg_cadence = int(act.get('averageRunningCadenceInStepsPerMinute', 0)) if act.get('averageRunningCadenceInStepsPerMinute') else None
        max_cadence = int(act.get('maxRunningCadenceInStepsPerMinute', 0)) if act.get('maxRunningCadenceInStepsPerMinute') else None
        avg_stride_length_cm = float(act.get('avgStrideLength', 0)) if act.get('avgStrideLength') else None
        avg_vertical_oscillation_cm = float(act.get('avgVerticalOscillation', 0)) if act.get('avgVerticalOscillation') else None
        avg_ground_contact_time_ms = int(act.get('avgGroundContactTime', 0)) if act.get('avgGroundContactTime') else None
        vertical_ratio_percent = float(act.get('avgVerticalRatio', 0)) if act.get('avgVerticalRatio') else None
        total_steps = int(act.get('steps', 0)) if act.get('steps') else None

        # 功率指标
        avg_power_watts = int(act.get('avgPower', 0)) if act.get('avgPower') else None
        max_power_watts = int(act.get('maxPower', 0)) if act.get('maxPower') else None
        normalized_power_watts = int(act.get('normPower', 0)) if act.get('normPower') else None
        power_zone_1_seconds = int(act.get('powerTimeInZone_1', 0)) if act.get('powerTimeInZone_1') else None
        power_zone_2_seconds = int(act.get('powerTimeInZone_2', 0)) if act.get('powerTimeInZone_2') else None
        power_zone_3_seconds = int(act.get('powerTimeInZone_3', 0)) if act.get('powerTimeInZone_3') else None
        power_zone_4_seconds = int(act.get('powerTimeInZone_4', 0)) if act.get('powerTimeInZone_4') else None
        power_zone_5_seconds = int(act.get('powerTimeInZone_5', 0)) if act.get('powerTimeInZone_5') else None

        # 速度指标
        avg_speed_mps = float(act.get('averageSpeed', 0)) if act.get('averageSpeed') else None
        max_speed_mps = float(act.get('maxSpeed', 0)) if act.get('maxSpeed') else None

        # 训练效果指标
        aerobic_training_effect = float(act.get('aerobicTrainingEffect', 0)) if act.get('aerobicTrainingEffect') else None
        anaerobic_training_effect = float(act.get('anaerobicTrainingEffect', 0)) if act.get('anaerobicTrainingEffect') else None
        training_effect_label = act.get('trainingEffectLabel', None)
        training_load = int(act.get('activityTrainingLoad', 0)) if act.get('activityTrainingLoad') else None

        # 卡路里和代谢指标
        activity_calories = int(act.get('calories', 0)) if act.get('calories') else None
        basal_metabolism_calories = int(act.get('bmrCalories', 0)) if act.get('bmrCalories') else None
        estimated_sweat_loss_ml = int(act.get('waterEstimated', 0)) if act.get('waterEstimated') else None

        # 强度时长
        moderate_intensity_minutes = int(act.get('moderateIntensityMinutes', 0)) if act.get('moderateIntensityMinutes') else None
        vigorous_intensity_minutes = int(act.get('vigorousIntensityMinutes', 0)) if act.get('vigorousIntensityMinutes') else None

        # 其他指标
        body_battery_change = int(act.get('differenceBodyBattery', 0)) if act.get('differenceBodyBattery') else None

        # 元数据
        current_ts = int(time.time())

        # 完全匹配training_records_garmin表结构
        return {
            'user_id': 'default_user',
            'activity_id': activity_id,
            'activity_name': activity_name,
            'sport_type': sport_type,
            'start_time_gmt': start_time_gmt,
            'end_time_gmt': end_time_gmt,
            'duration_seconds': duration_seconds,
            'distance_meters': distance_meters,
            'avg_heart_rate': avg_heart_rate,
            'max_heart_rate': max_heart_rate,
            'hr_zone_1_seconds': hr_zone_1_seconds,
            'hr_zone_2_seconds': hr_zone_2_seconds,
            'hr_zone_3_seconds': hr_zone_3_seconds,
            'hr_zone_4_seconds': hr_zone_4_seconds,
            'hr_zone_5_seconds': hr_zone_5_seconds,
            'avg_cadence': avg_cadence,
            'max_cadence': max_cadence,
            'avg_stride_length_cm': avg_stride_length_cm,
            'avg_vertical_oscillation_cm': avg_vertical_oscillation_cm,
            'avg_ground_contact_time_ms': avg_ground_contact_time_ms,
            'vertical_ratio_percent': vertical_ratio_percent,
            'total_steps': total_steps,
            'avg_power_watts': avg_power_watts,
            'max_power_watts': max_power_watts,
            'normalized_power_watts': normalized_power_watts,
            'power_zone_1_seconds': power_zone_1_seconds,
            'power_zone_2_seconds': power_zone_2_seconds,
            'power_zone_3_seconds': power_zone_3_seconds,
            'power_zone_4_seconds': power_zone_4_seconds,
            'power_zone_5_seconds': power_zone_5_seconds,
            'avg_speed_mps': avg_speed_mps,
            'max_speed_mps': max_speed_mps,
            'aerobic_training_effect': aerobic_training_effect,
            'anaerobic_training_effect': anaerobic_training_effect,
            'training_effect_label': training_effect_label,
            'training_load': training_load,
            'activity_calories': activity_calories,
            'basal_metabolism_calories': basal_metabolism_calories,
            'estimated_sweat_loss_ml': estimated_sweat_loss_ml,
            'moderate_intensity_minutes': moderate_intensity_minutes,
            'vigorous_intensity_minutes': vigorous_intensity_minutes,
            'body_battery_change': body_battery_change,
            'add_ts': current_ts,
            'last_modify_ts': current_ts,
            'data_source': 'garmin_connect'
        }

    def import_to_database(self, activities: list, truncate_first: bool = True) -> dict:
        """
        导入数据到数据库

        Args:
            activities: 活动数据列表
            truncate_first: 是否先清空表(覆盖写入)

        Returns:
            dict: 导入统计 {'success': int, 'failed': int, 'total': int}
        """
        if not activities:
            return {'success': 0, 'failed': 0, 'total': 0}

        # 创建训练记录管理器
        record_manager = TrainingRecordManager(data_source='garmin')
        # 动态获取SessionLocal，确保使用最新的数据库配置
        SessionLocal = get_session_local()
        session = SessionLocal()

        success_count = 0
        failed_count = 0

        try:
            # 是否清空表
            if truncate_first:
                Model = record_manager.get_model_class()
                deleted_count = session.query(Model).delete()
                session.commit()

            # 逐条导入
            for i, act in enumerate(activities, 1):
                try:
                    # 解析活动数据
                    record_data = self.parse_activity(act)
                    if not record_data:
                        failed_count += 1
                        continue

                    # 创建记录
                    record = record_manager.create_record(**record_data)
                    session.add(record)
                    session.commit()

                    success_count += 1

                except Exception as e:
                    session.rollback()
                    failed_count += 1
                    continue

            return {
                'success': success_count,
                'failed': failed_count,
                'total': len(activities)
            }

        except Exception as e:
            session.rollback()
            return {'success': 0, 'failed': len(activities), 'total': len(activities)}
        finally:
            session.close()

    def run(self, truncate_first: bool = True) -> dict:
        """
        执行完整的Garmin数据导入流程

        Args:
            truncate_first: 是否先清空表(覆盖写入)

        Returns:
            dict: 导入统计
        """
        # 登录
        if not self.login():
            return {'success': 0, 'failed': 0, 'total': 0, 'error': '登录失败'}

        # 抓取数据
        activities = self.fetch_activities()
        if not activities:
            return {'success': 0, 'failed': 0, 'total': 0, 'error': '没有可导入的跑步数据'}

        # 导入数据库
        result = self.import_to_database(activities, truncate_first)
        return result
