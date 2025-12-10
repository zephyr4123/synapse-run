# -*- coding: utf-8 -*-
"""
Garmin设备训练数据搜索工具 (ORM版本)
基于SQLAlchemy ORM实现,替代原生SQL,避免SQL注入风险
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from sqlalchemy import func, case
from sqlalchemy.orm import Session

from .base_search import BaseTrainingDataSearch, DBResponse
from .db_models import TrainingRecordGarmin
from .db_session import db_session_manager


@dataclass
class GarminTrainingRecord:
    """Garmin训练记录数据类"""
    id: int
    user_id: str

    # 基础训练信息
    activity_id: Optional[str]
    activity_name: Optional[str]
    sport_type: str
    start_time_gmt: datetime
    end_time_gmt: datetime
    duration_seconds: int
    distance_meters: Optional[float]

    # 心率指标
    avg_heart_rate: Optional[int]
    max_heart_rate: Optional[int]
    hr_zone_1_seconds: Optional[int]
    hr_zone_2_seconds: Optional[int]
    hr_zone_3_seconds: Optional[int]
    hr_zone_4_seconds: Optional[int]
    hr_zone_5_seconds: Optional[int]

    # 步频步幅指标
    avg_cadence: Optional[int]
    max_cadence: Optional[int]
    avg_stride_length_cm: Optional[float]
    avg_vertical_oscillation_cm: Optional[float]
    avg_ground_contact_time_ms: Optional[int]
    vertical_ratio_percent: Optional[float]
    total_steps: Optional[int]

    # 功率指标
    avg_power_watts: Optional[int]
    max_power_watts: Optional[int]
    normalized_power_watts: Optional[int]
    power_zone_1_seconds: Optional[int]
    power_zone_2_seconds: Optional[int]
    power_zone_3_seconds: Optional[int]
    power_zone_4_seconds: Optional[int]
    power_zone_5_seconds: Optional[int]

    # 速度指标
    avg_speed_mps: Optional[float]
    max_speed_mps: Optional[float]

    # 训练效果指标
    aerobic_training_effect: Optional[float]
    anaerobic_training_effect: Optional[float]
    training_effect_label: Optional[str]
    training_load: Optional[int]

    # 卡路里和代谢指标
    activity_calories: Optional[int]
    basal_metabolism_calories: Optional[int]
    estimated_sweat_loss_ml: Optional[int]

    # 强度时长
    moderate_intensity_minutes: Optional[int]
    vigorous_intensity_minutes: Optional[int]

    # 其他指标
    body_battery_change: Optional[int]

    # 元数据
    add_ts: int
    last_modify_ts: int
    data_source: str

    # 计算字段
    pace_per_km: Optional[float] = None


class GarminDataSearch(BaseTrainingDataSearch):
    """Garmin数据源搜索工具 (ORM版本)"""

    def __init__(self):
        super().__init__(data_source="garmin")
        self.db_manager = db_session_manager

    def _load_db_config(self) -> Dict[str, Any]:
        """ORM方式不需要直接配置,返回空字典"""
        return {}

    def _validate_config(self):
        """ORM方式由db_session_manager统一验证"""
        pass

    def _execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """ORM方式不使用原生SQL,此方法保留仅为兼容基类"""
        raise NotImplementedError("ORM方式不使用_execute_query方法")

    def _orm_to_record(self, orm_obj: TrainingRecordGarmin) -> GarminTrainingRecord:
        """将ORM对象转换为GarminTrainingRecord数据类"""
        pace = self._calculate_pace(orm_obj.duration_seconds, orm_obj.distance_meters)
        return GarminTrainingRecord(
            id=orm_obj.id,
            user_id=orm_obj.user_id,
            activity_id=orm_obj.activity_id,
            activity_name=orm_obj.activity_name,
            sport_type=orm_obj.sport_type,
            start_time_gmt=orm_obj.start_time_gmt,
            end_time_gmt=orm_obj.end_time_gmt,
            duration_seconds=orm_obj.duration_seconds,
            distance_meters=orm_obj.distance_meters,
            # 心率指标
            avg_heart_rate=orm_obj.avg_heart_rate,
            max_heart_rate=orm_obj.max_heart_rate,
            hr_zone_1_seconds=orm_obj.hr_zone_1_seconds,
            hr_zone_2_seconds=orm_obj.hr_zone_2_seconds,
            hr_zone_3_seconds=orm_obj.hr_zone_3_seconds,
            hr_zone_4_seconds=orm_obj.hr_zone_4_seconds,
            hr_zone_5_seconds=orm_obj.hr_zone_5_seconds,
            # 步频步幅指标
            avg_cadence=orm_obj.avg_cadence,
            max_cadence=orm_obj.max_cadence,
            avg_stride_length_cm=orm_obj.avg_stride_length_cm,
            avg_vertical_oscillation_cm=orm_obj.avg_vertical_oscillation_cm,
            avg_ground_contact_time_ms=orm_obj.avg_ground_contact_time_ms,
            vertical_ratio_percent=orm_obj.vertical_ratio_percent,
            total_steps=orm_obj.total_steps,
            # 功率指标
            avg_power_watts=orm_obj.avg_power_watts,
            max_power_watts=orm_obj.max_power_watts,
            normalized_power_watts=orm_obj.normalized_power_watts,
            power_zone_1_seconds=orm_obj.power_zone_1_seconds,
            power_zone_2_seconds=orm_obj.power_zone_2_seconds,
            power_zone_3_seconds=orm_obj.power_zone_3_seconds,
            power_zone_4_seconds=orm_obj.power_zone_4_seconds,
            power_zone_5_seconds=orm_obj.power_zone_5_seconds,
            # 速度指标
            avg_speed_mps=orm_obj.avg_speed_mps,
            max_speed_mps=orm_obj.max_speed_mps,
            # 训练效果指标
            aerobic_training_effect=orm_obj.aerobic_training_effect,
            anaerobic_training_effect=orm_obj.anaerobic_training_effect,
            training_effect_label=orm_obj.training_effect_label,
            training_load=orm_obj.training_load,
            # 卡路里和代谢指标
            activity_calories=orm_obj.activity_calories,
            basal_metabolism_calories=orm_obj.basal_metabolism_calories,
            estimated_sweat_loss_ml=orm_obj.estimated_sweat_loss_ml,
            # 强度时长
            moderate_intensity_minutes=orm_obj.moderate_intensity_minutes,
            vigorous_intensity_minutes=orm_obj.vigorous_intensity_minutes,
            # 其他指标
            body_battery_change=orm_obj.body_battery_change,
            # 元数据
            add_ts=orm_obj.add_ts,
            last_modify_ts=orm_obj.last_modify_ts,
            data_source=orm_obj.data_source,
            pace_per_km=pace
        )

    def search_recent_trainings(
        self,
        days: int = 7,
        limit: int = 50
    ) -> DBResponse:
        """查询最近训练记录 (ORM方式)"""
        params_for_log = {'days': days, 'limit': limit}
        print(f"--- Garmin数据源(ORM): 查询最近训练���录 (params: {params_for_log}) ---")

        start_time = datetime.now() - timedelta(days=days)

        try:
            with self.db_manager.get_session() as session:
                query = session.query(TrainingRecordGarmin)\
                    .filter(TrainingRecordGarmin.start_time_gmt >= start_time)\
                    .order_by(TrainingRecordGarmin.start_time_gmt.desc())\
                    .limit(limit)

                orm_results = query.all()
                records = [self._orm_to_record(obj) for obj in orm_results]

            return DBResponse(
                tool_name="search_recent_trainings",
                parameters=params_for_log,
                data_source=self.data_source,
                results=records
            )
        except Exception as e:
            print(f"Garmin数据源(ORM)查询错误: {e}")
            return DBResponse(
                tool_name="search_recent_trainings",
                parameters=params_for_log,
                data_source=self.data_source,
                error_message=str(e)
            )

    def search_by_date_range(
        self,
        start_date: str,
        end_date: str,
        limit: int = 100
    ) -> DBResponse:
        """按日期范围查询 (ORM方式)"""
        params_for_log = {
            'start_date': start_date,
            'end_date': end_date,
            'limit': limit
        }
        print(f"--- Garmin数据源(ORM): 按日期范围查询 (params: {params_for_log}) ---")

        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        except ValueError:
            return DBResponse(
                tool_name="search_by_date_range",
                parameters=params_for_log,
                data_source=self.data_source,
                error_message="日期格式错误,请使用 'YYYY-MM-DD' 格式"
            )

        try:
            with self.db_manager.get_session() as session:
                query = session.query(TrainingRecordGarmin)\
                    .filter(
                        TrainingRecordGarmin.start_time_gmt >= start_dt,
                        TrainingRecordGarmin.start_time_gmt < end_dt
                    )\
                    .order_by(TrainingRecordGarmin.start_time_gmt.desc())\
                    .limit(limit)

                orm_results = query.all()
                records = [self._orm_to_record(obj) for obj in orm_results]

            return DBResponse(
                tool_name="search_by_date_range",
                parameters=params_for_log,
                data_source=self.data_source,
                results=records
            )
        except Exception as e:
            print(f"Garmin数据源(ORM)查询错误: {e}")
            return DBResponse(
                tool_name="search_by_date_range",
                parameters=params_for_log,
                data_source=self.data_source,
                error_message=str(e)
            )

    def get_training_stats(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> DBResponse:
        """获取训练统计 (ORM方式,包含Garmin扩展指标)"""
        params_for_log = {
            'start_date': start_date,
            'end_date': end_date
        }
        print(f"--- Garmin数据源(ORM): 获取训练统计 (params: {params_for_log}) ---")

        try:
            with self.db_manager.get_session() as session:
                query = session.query(
                    func.count(TrainingRecordGarmin.id).label('total_sessions'),
                    func.sum(TrainingRecordGarmin.duration_seconds).label('total_duration'),
                    func.avg(TrainingRecordGarmin.duration_seconds).label('avg_duration'),
                    func.sum(TrainingRecordGarmin.distance_meters).label('total_distance'),
                    func.avg(TrainingRecordGarmin.distance_meters).label('avg_distance'),
                    func.avg(TrainingRecordGarmin.avg_heart_rate).label('overall_avg_heart_rate'),
                    func.max(TrainingRecordGarmin.max_heart_rate).label('peak_heart_rate'),
                    func.avg(TrainingRecordGarmin.avg_cadence).label('overall_avg_cadence'),
                    func.avg(TrainingRecordGarmin.avg_power_watts).label('overall_avg_power'),
                    func.avg(TrainingRecordGarmin.training_load).label('avg_training_load'),
                    func.avg(TrainingRecordGarmin.aerobic_training_effect).label('avg_aerobic_effect'),
                    func.avg(TrainingRecordGarmin.anaerobic_training_effect).label('avg_anaerobic_effect'),
                    func.sum(TrainingRecordGarmin.activity_calories).label('total_calories'),
                    func.avg(TrainingRecordGarmin.avg_stride_length_cm).label('avg_stride_length'),
                    func.avg(TrainingRecordGarmin.avg_vertical_oscillation_cm).label('avg_vertical_oscillation'),
                    func.avg(TrainingRecordGarmin.avg_ground_contact_time_ms).label('avg_ground_contact_time')
                )

                # 添加日期过滤
                if start_date:
                    try:
                        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                        query = query.filter(TrainingRecordGarmin.start_time_gmt >= start_dt)
                    except ValueError:
                        return DBResponse(
                            tool_name="get_training_stats",
                            parameters=params_for_log,
                            data_source=self.data_source,
                            error_message="开始日期格式错误"
                        )

                if end_date:
                    try:
                        end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                        query = query.filter(TrainingRecordGarmin.start_time_gmt < end_dt)
                    except ValueError:
                        return DBResponse(
                            tool_name="get_training_stats",
                            parameters=params_for_log,
                            data_source=self.data_source,
                            error_message="结束日期格式错误"
                        )

                result = query.first()
                if not result or result.total_sessions == 0:
                    return DBResponse(
                        tool_name="get_training_stats",
                        parameters=params_for_log,
                        data_source=self.data_source,
                        error_message="未找到数据"
                    )

                # 转换为字典并计算平均配速
                stats = {
                    'total_sessions': result.total_sessions,
                    'total_duration': result.total_duration,
                    'avg_duration': result.avg_duration,
                    'total_distance': result.total_distance,
                    'avg_distance': result.avg_distance,
                    'overall_avg_heart_rate': result.overall_avg_heart_rate,
                    'peak_heart_rate': result.peak_heart_rate,
                    'overall_avg_cadence': result.overall_avg_cadence,
                    'overall_avg_power': result.overall_avg_power,
                    'avg_training_load': result.avg_training_load,
                    'avg_aerobic_effect': result.avg_aerobic_effect,
                    'avg_anaerobic_effect': result.avg_anaerobic_effect,
                    'total_calories': result.total_calories,
                    'avg_stride_length': result.avg_stride_length,
                    'avg_vertical_oscillation': result.avg_vertical_oscillation,
                    'avg_ground_contact_time': result.avg_ground_contact_time
                }

                if stats['total_distance'] and stats['total_distance'] > 0:
                    total_distance_km = float(stats['total_distance']) / 1000.0
                    total_duration = float(stats['total_duration']) if stats['total_duration'] else 0.0
                    avg_pace = total_duration / total_distance_km
                    stats['avg_pace_per_km'] = round(avg_pace, 2)
                else:
                    stats['avg_pace_per_km'] = None

            return DBResponse(
                tool_name="get_training_stats",
                parameters=params_for_log,
                data_source=self.data_source,
                statistics=stats
            )
        except Exception as e:
            print(f"Garmin数据源(ORM)查询错误: {e}")
            return DBResponse(
                tool_name="get_training_stats",
                parameters=params_for_log,
                data_source=self.data_source,
                error_message=str(e)
            )

    def search_by_distance_range(
        self,
        min_distance_km: float,
        max_distance_km: Optional[float] = None,
        limit: int = 50
    ) -> DBResponse:
        """按距离范围查询 (ORM方式)"""
        params_for_log = {
            'min_distance_km': min_distance_km,
            'max_distance_km': max_distance_km,
            'limit': limit
        }
        print(f"--- Garmin数据源(ORM): 按距离范围查询 (params: {params_for_log}) ---")

        min_meters = min_distance_km * 1000

        try:
            with self.db_manager.get_session() as session:
                query = session.query(TrainingRecordGarmin)\
                    .filter(TrainingRecordGarmin.distance_meters >= min_meters)

                if max_distance_km:
                    max_meters = max_distance_km * 1000
                    query = query.filter(TrainingRecordGarmin.distance_meters <= max_meters)

                query = query.order_by(TrainingRecordGarmin.distance_meters.desc()).limit(limit)

                orm_results = query.all()
                records = [self._orm_to_record(obj) for obj in orm_results]

            return DBResponse(
                tool_name="search_by_distance_range",
                parameters=params_for_log,
                data_source=self.data_source,
                results=records
            )
        except Exception as e:
            print(f"Garmin数据源(ORM)查询错误: {e}")
            return DBResponse(
                tool_name="search_by_distance_range",
                parameters=params_for_log,
                data_source=self.data_source,
                error_message=str(e)
            )

    def search_by_heart_rate(
        self,
        min_avg_hr: int,
        max_avg_hr: Optional[int] = None,
        limit: int = 50
    ) -> DBResponse:
        """按心率区间查询 (ORM方式)"""
        params_for_log = {
            'min_avg_hr': min_avg_hr,
            'max_avg_hr': max_avg_hr,
            'limit': limit
        }
        print(f"--- Garmin数据源(ORM): 按心率区间查询 (params: {params_for_log}) ---")

        try:
            with self.db_manager.get_session() as session:
                query = session.query(TrainingRecordGarmin)\
                    .filter(TrainingRecordGarmin.avg_heart_rate >= min_avg_hr)

                if max_avg_hr:
                    query = query.filter(TrainingRecordGarmin.avg_heart_rate <= max_avg_hr)

                query = query.order_by(TrainingRecordGarmin.start_time_gmt.desc()).limit(limit)

                orm_results = query.all()
                records = [self._orm_to_record(obj) for obj in orm_results]

            return DBResponse(
                tool_name="search_by_heart_rate",
                parameters=params_for_log,
                data_source=self.data_source,
                results=records
            )
        except Exception as e:
            print(f"Garmin数据源(ORM)查询错误: {e}")
            return DBResponse(
                tool_name="search_by_heart_rate",
                parameters=params_for_log,
                data_source=self.data_source,
                error_message=str(e)
            )

    # ===== Garmin��属扩展工具 =====

    def search_by_training_load(
        self,
        min_load: int,
        max_load: Optional[int] = None,
        limit: int = 50
    ) -> DBResponse:
        """按训练负荷查询 (ORM方式,Garmin专属)"""
        params_for_log = {
            'min_load': min_load,
            'max_load': max_load,
            'limit': limit
        }
        print(f"--- Garmin数据源(ORM): 按训练负荷查询 (params: {params_for_log}) ---")

        try:
            with self.db_manager.get_session() as session:
                query = session.query(TrainingRecordGarmin)\
                    .filter(TrainingRecordGarmin.training_load >= min_load)

                if max_load:
                    query = query.filter(TrainingRecordGarmin.training_load <= max_load)

                query = query.order_by(TrainingRecordGarmin.training_load.desc()).limit(limit)

                orm_results = query.all()
                records = [self._orm_to_record(obj) for obj in orm_results]

            return DBResponse(
                tool_name="search_by_training_load",
                parameters=params_for_log,
                data_source=self.data_source,
                results=records
            )
        except Exception as e:
            print(f"Garmin数据源(ORM)查询错误: {e}")
            return DBResponse(
                tool_name="search_by_training_load",
                parameters=params_for_log,
                data_source=self.data_source,
                error_message=str(e)
            )

    def search_by_power_zone(
        self,
        min_avg_power: int,
        max_avg_power: Optional[int] = None,
        limit: int = 50
    ) -> DBResponse:
        """按功率区间查询 (ORM方式,Garmin专属)"""
        params_for_log = {
            'min_avg_power': min_avg_power,
            'max_avg_power': max_avg_power,
            'limit': limit
        }
        print(f"--- Garmin数据源(ORM): 按功率区间查询 (params: {params_for_log}) ---")

        try:
            with self.db_manager.get_session() as session:
                query = session.query(TrainingRecordGarmin)\
                    .filter(TrainingRecordGarmin.avg_power_watts >= min_avg_power)

                if max_avg_power:
                    query = query.filter(TrainingRecordGarmin.avg_power_watts <= max_avg_power)

                query = query.order_by(TrainingRecordGarmin.avg_power_watts.desc()).limit(limit)

                orm_results = query.all()
                records = [self._orm_to_record(obj) for obj in orm_results]

            return DBResponse(
                tool_name="search_by_power_zone",
                parameters=params_for_log,
                data_source=self.data_source,
                results=records
            )
        except Exception as e:
            print(f"Garmin数据源(ORM)查询错误: {e}")
            return DBResponse(
                tool_name="search_by_power_zone",
                parameters=params_for_log,
                data_source=self.data_source,
                error_message=str(e)
            )

    def get_training_effect_analysis(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> DBResponse:
        """获取训练效果分析 (ORM方式,Garmin专属)"""
        params_for_log = {'start_date': start_date, 'end_date': end_date}
        print(f"--- Garmin数据源(ORM): 训练效果分析 (params: {params_for_log}) ---")

        try:
            with self.db_manager.get_session() as session:
                query = session.query(
                    func.count(TrainingRecordGarmin.id).label('total_sessions'),
                    func.avg(TrainingRecordGarmin.aerobic_training_effect).label('avg_aerobic_effect'),
                    func.avg(TrainingRecordGarmin.anaerobic_training_effect).label('avg_anaerobic_effect'),
                    func.avg(TrainingRecordGarmin.training_load).label('avg_training_load'),
                    func.sum(
                        case(
                            (TrainingRecordGarmin.training_effect_label.like('%Maintaining%'), 1),
                            else_=0
                        )
                    ).label('maintaining_count'),
                    func.sum(
                        case(
                            (TrainingRecordGarmin.training_effect_label.like('%Improving%'), 1),
                            else_=0
                        )
                    ).label('improving_count'),
                    func.sum(
                        case(
                            (TrainingRecordGarmin.training_effect_label.like('%Highly Improving%'), 1),
                            else_=0
                        )
                    ).label('highly_improving_count'),
                    func.sum(TrainingRecordGarmin.moderate_intensity_minutes).label('total_moderate_minutes'),
                    func.sum(TrainingRecordGarmin.vigorous_intensity_minutes).label('total_vigorous_minutes')
                )

                # 添加日期过滤
                if start_date:
                    try:
                        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                        query = query.filter(TrainingRecordGarmin.start_time_gmt >= start_dt)
                    except ValueError:
                        return DBResponse(
                            tool_name="get_training_effect_analysis",
                            parameters=params_for_log,
                            data_source=self.data_source,
                            error_message="开始日期格式错误"
                        )

                if end_date:
                    try:
                        end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                        query = query.filter(TrainingRecordGarmin.start_time_gmt < end_dt)
                    except ValueError:
                        return DBResponse(
                            tool_name="get_training_effect_analysis",
                            parameters=params_for_log,
                            data_source=self.data_source,
                            error_message="结束日期格式错误"
                        )

                result = query.first()
                if not result or result.total_sessions == 0:
                    return DBResponse(
                        tool_name="get_training_effect_analysis",
                        parameters=params_for_log,
                        data_source=self.data_source,
                        error_message="未找到数据"
                    )

                stats = {
                    'total_sessions': result.total_sessions,
                    'avg_aerobic_effect': result.avg_aerobic_effect,
                    'avg_anaerobic_effect': result.avg_anaerobic_effect,
                    'avg_training_load': result.avg_training_load,
                    'maintaining_count': result.maintaining_count,
                    'improving_count': result.improving_count,
                    'highly_improving_count': result.highly_improving_count,
                    'total_moderate_minutes': result.total_moderate_minutes,
                    'total_vigorous_minutes': result.total_vigorous_minutes
                }

            return DBResponse(
                tool_name="get_training_effect_analysis",
                parameters=params_for_log,
                data_source=self.data_source,
                statistics=stats
            )
        except Exception as e:
            print(f"Garmin数据源(ORM)查询错误: {e}")
            return DBResponse(
                tool_name="get_training_effect_analysis",
                parameters=params_for_log,
                data_source=self.data_source,
                error_message=str(e)
            )

    def get_supported_tools(self) -> List[str]:
        """获取Garmin数据源支持的所有工具"""
        base_tools = super().get_supported_tools()
        garmin_tools = [
            "search_by_training_load",
            "search_by_power_zone",
            "get_training_effect_analysis"
        ]
        return base_tools + garmin_tools
