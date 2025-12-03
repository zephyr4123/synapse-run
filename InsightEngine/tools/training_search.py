"""
专为中长跑训练计划定制的AI Agent数据库查询工具集 (TrainingDataDB)

版本: 1.0
最后更新: 2025-12-03

此脚本将用户的历史训练记录查询功能封装成一系列目标明确、参数清晰的独立工具,
专为AI Agent调用而设计。Agent可根据任务意图(如查询最近训练、统计月度数据、
分析心率区间、查找长距离训练)选择合适的工具,无需编写复杂的SQL语句。

主要工具:
- search_recent_trainings: 查询最近N天的训练记录
- search_by_date_range: 按日期范围查询训练记录
- get_training_stats: 获取统计数据(总距离、平均配速等)
- search_by_distance_range: 查找特定距离范围的训练
- search_by_heart_rate: 按心率区间查询训练
- get_exercise_type_summary: 按运动类型汇总统计
"""

import os
import json
import pymysql
import pymysql.cursors
from typing import List, Dict, Any, Optional, Literal
from dataclasses import dataclass, field
from datetime import datetime, timedelta

# --- 1. 数据结构定义 ---

@dataclass
class TrainingRecord:
    """训练记录数据类"""
    id: int
    exercise_type: str
    duration_seconds: int
    start_time: datetime
    end_time: datetime
    calories: Optional[int] = None
    distance_meters: Optional[float] = None
    avg_heart_rate: Optional[int] = None
    max_heart_rate: Optional[int] = None
    heart_rate_data: Optional[List[int]] = None
    pace_per_km: Optional[float] = None  # 计算字段: 配速(秒/公里)
    user_id: str = "default_user"

@dataclass
class DBResponse:
    """封装工具的完整返回结果"""
    tool_name: str
    parameters: Dict[str, Any]
    results: List[TrainingRecord] = field(default_factory=list)
    results_count: int = 0
    statistics: Optional[Dict[str, Any]] = None  # 统计数据
    error_message: Optional[str] = None

# --- 2. 核心客户端与专用工具集 ---

class TrainingDataDB:
    """包含多种专用训练数据查询工具的客户端"""

    def __init__(self):
        """
        初始化客户端。连接信息从环境变量自动读取:
        - DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
        - DB_PORT (可选, 默认 3306)
        - DB_CHARSET (可选, 默认 utf8mb4)
        """
        self.db_config = {
            'host': os.getenv("DB_HOST"),
            'user': os.getenv("DB_USER"),
            'password': os.getenv("DB_PASSWORD"),
            'db': os.getenv("DB_NAME"),
            'port': int(os.getenv("DB_PORT", 3306)),
            'charset': os.getenv("DB_CHARSET", "utf8mb4"),
            'cursorclass': pymysql.cursors.DictCursor
        }
        required = ['host', 'user', 'password', 'db']
        if missing := [k for k in required if not self.db_config[k]]:
            raise ValueError(
                f"数据库配置缺失! 请设置环境变量: {', '.join([f'DB_{k.upper()}' for k in missing])}"
            )

    def _execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """执行SQL查询"""
        conn = None
        try:
            conn = pymysql.connect(**self.db_config)
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                return cursor.fetchall()
        except pymysql.Error as e:
            print(f"数据库查询时发生错误: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def _parse_heart_rate_data(self, hr_json: Optional[str]) -> Optional[List[int]]:
        """解析心率JSON数据"""
        if not hr_json:
            return None
        try:
            data = json.loads(hr_json)
            return [int(x) for x in data if x]
        except (json.JSONDecodeError, ValueError):
            return None

    def _calculate_pace(self, duration_seconds: int, distance_meters: Optional[float]) -> Optional[float]:
        """计算配速(秒/公里)"""
        if not distance_meters or distance_meters <= 0:
            return None
        return duration_seconds / (distance_meters / 1000.0)

    def _row_to_record(self, row: Dict[str, Any]) -> TrainingRecord:
        """将数据库行转换为TrainingRecord对象"""
        pace = self._calculate_pace(row['duration_seconds'], row.get('distance_meters'))
        return TrainingRecord(
            id=row['id'],
            exercise_type=row['exercise_type'],
            duration_seconds=row['duration_seconds'],
            start_time=row['start_time'],
            end_time=row['end_time'],
            calories=row.get('calories'),
            distance_meters=row.get('distance_meters'),
            avg_heart_rate=row.get('avg_heart_rate'),
            max_heart_rate=row.get('max_heart_rate'),
            heart_rate_data=self._parse_heart_rate_data(row.get('heart_rate_data')),
            pace_per_km=pace,
            user_id=row.get('user_id', 'default_user')
        )

    def search_recent_trainings(
        self,
        days: int = 7,
        exercise_type: Optional[str] = None,
        limit: int = 50
    ) -> DBResponse:
        """
        【工具】查询最近训练记录: 获取最近N天的训练数据

        Args:
            days (int): 查询最近多少天的数据,默认7天
            exercise_type (Optional[str]): 运动类型筛选,如'跑步',默认None(所有类型)
            limit (int): 返回结果的最大数量,默认50

        Returns:
            DBResponse: 包含训练记录列表
        """
        params_for_log = {'days': days, 'exercise_type': exercise_type, 'limit': limit}
        print(f"--- TOOL: 查询最近训练记录 (params: {params_for_log}) ---")

        start_time = datetime.now() - timedelta(days=days)
        query = """
            SELECT * FROM training_records
            WHERE start_time >= %s
        """
        params = [start_time]

        if exercise_type:
            query += " AND exercise_type = %s"
            params.append(exercise_type)

        query += " ORDER BY start_time DESC LIMIT %s"
        params.append(limit)

        raw_results = self._execute_query(query, tuple(params))
        records = [self._row_to_record(row) for row in raw_results]

        return DBResponse(
            "search_recent_trainings",
            params_for_log,
            results=records,
            results_count=len(records)
        )

    def search_by_date_range(
        self,
        start_date: str,
        end_date: str,
        exercise_type: Optional[str] = None,
        limit: int = 100
    ) -> DBResponse:
        """
        【工具】按日期范围查询: 在指定时间段内查询训练记录

        Args:
            start_date (str): 开始日期,格式 'YYYY-MM-DD'
            end_date (str): 结束日期,格式 'YYYY-MM-DD'
            exercise_type (Optional[str]): 运动类型筛选,默认None
            limit (int): 返回结果的最大数量,默认100

        Returns:
            DBResponse: 包含训练记录列表
        """
        params_for_log = {
            'start_date': start_date,
            'end_date': end_date,
            'exercise_type': exercise_type,
            'limit': limit
        }
        print(f"--- TOOL: 按日期范围查询 (params: {params_for_log}) ---")

        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        except ValueError:
            return DBResponse(
                "search_by_date_range",
                params_for_log,
                error_message="日期格式错误,请使用 'YYYY-MM-DD' 格式"
            )

        query = """
            SELECT * FROM training_records
            WHERE start_time >= %s AND start_time < %s
        """
        params = [start_dt, end_dt]

        if exercise_type:
            query += " AND exercise_type = %s"
            params.append(exercise_type)

        query += " ORDER BY start_time DESC LIMIT %s"
        params.append(limit)

        raw_results = self._execute_query(query, tuple(params))
        records = [self._row_to_record(row) for row in raw_results]

        return DBResponse(
            "search_by_date_range",
            params_for_log,
            results=records,
            results_count=len(records)
        )

    def get_training_stats(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        exercise_type: Optional[str] = None
    ) -> DBResponse:
        """
        【工具】获取训练统计: 计算总距离、平均配速、总时长等统计指标

        Args:
            start_date (Optional[str]): 开始日期,格式 'YYYY-MM-DD',默认None(全部数据)
            end_date (Optional[str]): 结束日期,格式 'YYYY-MM-DD',默认None
            exercise_type (Optional[str]): 运动类型筛选,默认None

        Returns:
            DBResponse: statistics字段包含统计结果
        """
        params_for_log = {
            'start_date': start_date,
            'end_date': end_date,
            'exercise_type': exercise_type
        }
        print(f"--- TOOL: 获取训练统计 (params: {params_for_log}) ---")

        query = """
            SELECT
                COUNT(*) as total_sessions,
                SUM(duration_seconds) as total_duration,
                AVG(duration_seconds) as avg_duration,
                SUM(distance_meters) as total_distance,
                AVG(distance_meters) as avg_distance,
                AVG(avg_heart_rate) as overall_avg_heart_rate,
                MAX(max_heart_rate) as peak_heart_rate,
                SUM(calories) as total_calories
            FROM training_records
            WHERE 1=1
        """
        params = []

        if start_date:
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                query += " AND start_time >= %s"
                params.append(start_dt)
            except ValueError:
                return DBResponse(
                    "get_training_stats",
                    params_for_log,
                    error_message="开始日期格式错误"
                )

        if end_date:
            try:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                query += " AND start_time < %s"
                params.append(end_dt)
            except ValueError:
                return DBResponse(
                    "get_training_stats",
                    params_for_log,
                    error_message="结束日期格式错误"
                )

        if exercise_type:
            query += " AND exercise_type = %s"
            params.append(exercise_type)

        raw_results = self._execute_query(query, tuple(params))
        if not raw_results:
            return DBResponse(
                "get_training_stats",
                params_for_log,
                error_message="未找到数据"
            )

        stats = raw_results[0]
        # 计算平均配速
        if stats['total_distance'] and stats['total_distance'] > 0:
            avg_pace = stats['total_duration'] / (stats['total_distance'] / 1000.0)
            stats['avg_pace_per_km'] = round(avg_pace, 2)
        else:
            stats['avg_pace_per_km'] = None

        return DBResponse(
            "get_training_stats",
            params_for_log,
            statistics=stats,
            results_count=0
        )

    def search_by_distance_range(
        self,
        min_distance_km: float,
        max_distance_km: Optional[float] = None,
        exercise_type: Optional[str] = None,
        limit: int = 50
    ) -> DBResponse:
        """
        【工具】按距离范围查询: 查找特定距离范围的训练(如长距离跑)

        Args:
            min_distance_km (float): 最小距离(公里)
            max_distance_km (Optional[float]): 最大距离(公里),默认None(无上限)
            exercise_type (Optional[str]): 运动类型筛选,默认None
            limit (int): 返回结果的最大数量,默认50

        Returns:
            DBResponse: 包含训练记录列表
        """
        params_for_log = {
            'min_distance_km': min_distance_km,
            'max_distance_km': max_distance_km,
            'exercise_type': exercise_type,
            'limit': limit
        }
        print(f"--- TOOL: 按距离范围查询 (params: {params_for_log}) ---")

        min_meters = min_distance_km * 1000
        query = "SELECT * FROM training_records WHERE distance_meters >= %s"
        params = [min_meters]

        if max_distance_km:
            max_meters = max_distance_km * 1000
            query += " AND distance_meters <= %s"
            params.append(max_meters)

        if exercise_type:
            query += " AND exercise_type = %s"
            params.append(exercise_type)

        query += " ORDER BY distance_meters DESC LIMIT %s"
        params.append(limit)

        raw_results = self._execute_query(query, tuple(params))
        records = [self._row_to_record(row) for row in raw_results]

        return DBResponse(
            "search_by_distance_range",
            params_for_log,
            results=records,
            results_count=len(records)
        )

    def search_by_heart_rate(
        self,
        min_avg_hr: int,
        max_avg_hr: Optional[int] = None,
        exercise_type: Optional[str] = None,
        limit: int = 50
    ) -> DBResponse:
        """
        【工具】按心率区间查询: 按平均心率范围查找训练

        Args:
            min_avg_hr (int): 最小平均心率
            max_avg_hr (Optional[int]): 最大平均心率,默认None(无上限)
            exercise_type (Optional[str]): 运动类型筛选,默认None
            limit (int): 返回结果的最大数量,默认50

        Returns:
            DBResponse: 包含训练记录列表
        """
        params_for_log = {
            'min_avg_hr': min_avg_hr,
            'max_avg_hr': max_avg_hr,
            'exercise_type': exercise_type,
            'limit': limit
        }
        print(f"--- TOOL: 按心率区间查询 (params: {params_for_log}) ---")

        query = "SELECT * FROM training_records WHERE avg_heart_rate >= %s"
        params = [min_avg_hr]

        if max_avg_hr:
            query += " AND avg_heart_rate <= %s"
            params.append(max_avg_hr)

        if exercise_type:
            query += " AND exercise_type = %s"
            params.append(exercise_type)

        query += " ORDER BY start_time DESC LIMIT %s"
        params.append(limit)

        raw_results = self._execute_query(query, tuple(params))
        records = [self._row_to_record(row) for row in raw_results]

        return DBResponse(
            "search_by_heart_rate",
            params_for_log,
            results=records,
            results_count=len(records)
        )

    def get_exercise_type_summary(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> DBResponse:
        """
        【工具】按运动类型汇总: 按运动类型分组统计

        Args:
            start_date (Optional[str]): 开始日期,格式 'YYYY-MM-DD',默认None
            end_date (Optional[str]): 结束日期,格式 'YYYY-MM-DD',默认None

        Returns:
            DBResponse: statistics字段包含按类型分组的统计
        """
        params_for_log = {'start_date': start_date, 'end_date': end_date}
        print(f"--- TOOL: 按运动类型汇总 (params: {params_for_log}) ---")

        query = """
            SELECT
                exercise_type,
                COUNT(*) as sessions,
                SUM(duration_seconds) as total_duration,
                SUM(distance_meters) as total_distance,
                AVG(avg_heart_rate) as avg_heart_rate
            FROM training_records
            WHERE 1=1
        """
        params = []

        if start_date:
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                query += " AND start_time >= %s"
                params.append(start_dt)
            except ValueError:
                return DBResponse(
                    "get_exercise_type_summary",
                    params_for_log,
                    error_message="开始日期格式错误"
                )

        if end_date:
            try:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                query += " AND start_time < %s"
                params.append(end_dt)
            except ValueError:
                return DBResponse(
                    "get_exercise_type_summary",
                    params_for_log,
                    error_message="结束日期格式错误"
                )

        query += " GROUP BY exercise_type ORDER BY sessions DESC"

        raw_results = self._execute_query(query, tuple(params))
        return DBResponse(
            "get_exercise_type_summary",
            params_for_log,
            statistics={'by_type': raw_results},
            results_count=len(raw_results)
        )

# --- 3. 测试与使用示例 ---
def print_response_summary(response: DBResponse):
    """简化的打印函数,用于展示测试结果"""
    if response.error_message:
        print(f"工具 '{response.tool_name}' 执行出错: {response.error_message}")
        print("-" * 80)
        return

    params_str = ", ".join(f"{k}='{v}'" for k, v in response.parameters.items())
    print(f"查询: 工具='{response.tool_name}', 参数=[{params_str}]")

    if response.statistics:
        print(f"统计结果: {json.dumps(response.statistics, ensure_ascii=False, indent=2, default=str)}")

    if response.results:
        print(f"找到 {response.results_count} 条训练记录。")
        print("--- 前5条结果示例 ---")
        for i, rec in enumerate(response.results[:5]):
            distance_km = f"{rec.distance_meters/1000:.2f}km" if rec.distance_meters else "N/A"
            pace_str = f"{int(rec.pace_per_km//60)}'{int(rec.pace_per_km%60):02d}\"" if rec.pace_per_km else "N/A"
            print(
                f"{i+1}. [{rec.exercise_type}] {rec.start_time.strftime('%Y-%m-%d %H:%M')}\n"
                f"   距离: {distance_km}, 时长: {rec.duration_seconds//60}分{rec.duration_seconds%60}秒, 配速: {pace_str}/km\n"
                f"   平均心率: {rec.avg_heart_rate or 'N/A'}, 最大心率: {rec.max_heart_rate or 'N/A'}, 卡路里: {rec.calories or 'N/A'}"
            )
    print("-" * 80)

if __name__ == "__main__":
    try:
        db_tools = TrainingDataDB()
        print("训练数据库工具初始化成功,开始执行测试场景...\n")

        # 场景1: 查询最近7天的跑步记录
        response1 = db_tools.search_recent_trainings(days=7, exercise_type='跑步', limit=5)
        print_response_summary(response1)

        # 场景2: 查询最近30天的统计数据
        from datetime import date
        today = date.today()
        start_30d = (today - timedelta(days=30)).strftime('%Y-%m-%d')
        response2 = db_tools.get_training_stats(
            start_date=start_30d,
            end_date=today.strftime('%Y-%m-%d'),
            exercise_type='跑步'
        )
        print_response_summary(response2)

        # 场景3: 查询长距离训练(10公里以上)
        response3 = db_tools.search_by_distance_range(min_distance_km=10.0, limit=5)
        print_response_summary(response3)

        # 场景4: 按运动类型汇总
        response4 = db_tools.get_exercise_type_summary()
        print_response_summary(response4)

    except ValueError as e:
        print(f"初始化失败: {e}")
        print("请确保相关的数据库环境变量已正确设置。")
    except Exception as e:
        print(f"测试过程中发生未知错误: {e}")
        import traceback
        traceback.print_exc()
