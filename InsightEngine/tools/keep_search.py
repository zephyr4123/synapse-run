# -*- coding: utf-8 -*-
"""
Keep运动APP训练数据搜索工具 (ORM版本)
基于SQLAlchemy ORM实现,替代原生SQL,避免SQL注入风险
"""

import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from sqlalchemy import func

from .base_search import BaseTrainingDataSearch, DBResponse
from .db_models import TrainingRecordKeep
from .db_session import db_session_manager


@dataclass
class KeepTrainingRecord:
    """Keep训练记录数据类"""
    id: int
    user_id: str

    # 基础训练信息
    exercise_type: str
    duration_seconds: int
    start_time: datetime
    end_time: datetime

    # 运动指标
    calories: Optional[int]
    distance_meters: Optional[float]
    avg_heart_rate: Optional[int]
    max_heart_rate: Optional[int]

    # 详细数据 (JSON格式)
    heart_rate_data: Optional[List[int]]

    # 元数据
    add_ts: int
    last_modify_ts: int
    data_source: str

    # 计算字段
    pace_per_km: Optional[float] = None


class KeepDataSearch(BaseTrainingDataSearch):
    """Keep数据源搜索工具 (ORM版本)"""

    def __init__(self):
        super().__init__(data_source="keep")
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

    def _parse_heart_rate_data(self, hr_json: Optional[str]) -> Optional[List[int]]:
        """解析心率JSON数据"""
        if not hr_json:
            return None
        try:
            data = json.loads(hr_json)
            if data is None or not isinstance(data, (list, tuple)):
                return None
            result = []
            for x in data:
                if x is not None and x != '':
                    try:
                        result.append(int(x))
                    except (ValueError, TypeError):
                        continue
            return result if result else None
        except (json.JSONDecodeError, ValueError, TypeError):
            return None

    def _orm_to_record(self, orm_obj: TrainingRecordKeep) -> KeepTrainingRecord:
        """将ORM对象转换为KeepTrainingRecord数据类"""
        pace = self._calculate_pace(orm_obj.duration_seconds, orm_obj.distance_meters)
        return KeepTrainingRecord(
            id=orm_obj.id,
            user_id=orm_obj.user_id,
            exercise_type=orm_obj.exercise_type,
            duration_seconds=orm_obj.duration_seconds,
            start_time=orm_obj.start_time,
            end_time=orm_obj.end_time,
            calories=orm_obj.calories,
            distance_meters=orm_obj.distance_meters,
            avg_heart_rate=orm_obj.avg_heart_rate,
            max_heart_rate=orm_obj.max_heart_rate,
            heart_rate_data=self._parse_heart_rate_data(orm_obj.heart_rate_data),
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
        print(f"--- Keep数据源(ORM): 查询最近训练记录 (params: {params_for_log}) ---")

        start_time = datetime.now() - timedelta(days=days)

        try:
            with self.db_manager.get_session() as session:
                query = session.query(TrainingRecordKeep)\
                    .filter(TrainingRecordKeep.start_time >= start_time)\
                    .order_by(TrainingRecordKeep.start_time.desc())\
                    .limit(limit)

                orm_results = query.all()
                records = [self._orm_to_record(obj) for obj in orm_results]

            return DBResponse(
                tool_name="search_recent_trainings",
                parameters=params_for_log,
                data_source=self.data_source,
                results=records,
                results_count=len(records)
            )
        except Exception as e:
            print(f"Keep数据源(ORM)查询错误: {e}")
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
        print(f"--- Keep数据源(ORM): 按日期范围查询 (params: {params_for_log}) ---")

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
                query = session.query(TrainingRecordKeep)\
                    .filter(
                        TrainingRecordKeep.start_time >= start_dt,
                        TrainingRecordKeep.start_time < end_dt
                    )\
                    .order_by(TrainingRecordKeep.start_time.desc())\
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
            print(f"Keep数据源(ORM)查询错误: {e}")
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
        """获取训练统计 (ORM方式)"""
        params_for_log = {
            'start_date': start_date,
            'end_date': end_date
        }
        print(f"--- Keep数据源(ORM): 获取训练统计 (params: {params_for_log}) ---")

        try:
            with self.db_manager.get_session() as session:
                query = session.query(
                    func.count(TrainingRecordKeep.id).label('total_sessions'),
                    func.sum(TrainingRecordKeep.duration_seconds).label('total_duration'),
                    func.avg(TrainingRecordKeep.duration_seconds).label('avg_duration'),
                    func.sum(TrainingRecordKeep.distance_meters).label('total_distance'),
                    func.avg(TrainingRecordKeep.distance_meters).label('avg_distance'),
                    func.avg(TrainingRecordKeep.avg_heart_rate).label('overall_avg_heart_rate'),
                    func.max(TrainingRecordKeep.max_heart_rate).label('peak_heart_rate'),
                    func.sum(TrainingRecordKeep.calories).label('total_calories')
                )

                # 添加日期过滤
                if start_date:
                    try:
                        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                        query = query.filter(TrainingRecordKeep.start_time >= start_dt)
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
                        query = query.filter(TrainingRecordKeep.start_time < end_dt)
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
                    'total_calories': result.total_calories
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
            print(f"Keep数据源(ORM)查询错误: {e}")
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
        print(f"--- Keep数据源(ORM): 按距离范围查询 (params: {params_for_log}) ---")

        min_meters = min_distance_km * 1000

        try:
            with self.db_manager.get_session() as session:
                query = session.query(TrainingRecordKeep)\
                    .filter(TrainingRecordKeep.distance_meters >= min_meters)

                if max_distance_km:
                    max_meters = max_distance_km * 1000
                    query = query.filter(TrainingRecordKeep.distance_meters <= max_meters)

                query = query.order_by(TrainingRecordKeep.distance_meters.desc()).limit(limit)

                orm_results = query.all()
                records = [self._orm_to_record(obj) for obj in orm_results]

            return DBResponse(
                tool_name="search_by_distance_range",
                parameters=params_for_log,
                data_source=self.data_source,
                results=records
            )
        except Exception as e:
            print(f"Keep数据源(ORM)查询错误: {e}")
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
        print(f"--- Keep数据源(ORM): 按心率区间查询 (params: {params_for_log}) ---")

        try:
            with self.db_manager.get_session() as session:
                query = session.query(TrainingRecordKeep)\
                    .filter(TrainingRecordKeep.avg_heart_rate >= min_avg_hr)

                if max_avg_hr:
                    query = query.filter(TrainingRecordKeep.avg_heart_rate <= max_avg_hr)

                query = query.order_by(TrainingRecordKeep.start_time.desc()).limit(limit)

                orm_results = query.all()
                records = [self._orm_to_record(obj) for obj in orm_results]

            return DBResponse(
                tool_name="search_by_heart_rate",
                parameters=params_for_log,
                data_source=self.data_source,
                results=records
            )
        except Exception as e:
            print(f"Keep数据源(ORM)查询错误: {e}")
            return DBResponse(
                tool_name="search_by_heart_rate",
                parameters=params_for_log,
                data_source=self.data_source,
                error_message=str(e)
            )
