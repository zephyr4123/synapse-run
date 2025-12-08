#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
训练数据导入脚本
从Excel文件(406099.xlsx)导入训练记录到MySQL数据库

使用方法:
1. 确保数据库已创建training_records表 (执行training_tables.sql)
2. 设置环境变量: DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
3. 运行: python scripts/import_training_data.py

功能:
- 自动解析Excel文件
- 清洗数据(处理NaN值、时间格式转换)
- 批量导入到数据库
- 支持重复运行(使用INSERT IGNORE避免重复)
"""

import os
import sys
import json
import pymysql
import pandas as pd
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class TrainingDataImporter:
    """训练数据导入器"""

    def __init__(self, excel_path: str):
        self.excel_path = excel_path
        self.db_config = {
            'host': "localhost",
            'user': "huangsuxiang",
            'password': "Wodeshijie1.12",
            'db': "traningData",
            'port': 3306,
            'charset': "utf8mb4",
        }
        self._validate_db_config()

    def _validate_db_config(self):
        """验证数据库配置"""
        required = ['host', 'user', 'password', 'db']
        if missing := [k for k in required if not self.db_config[k]]:
            raise ValueError(
                f"数据库配置缺失! 请设置环境变量: {', '.join([f'DB_{k.upper()}' for k in missing])}"
            )

    def load_excel(self) -> pd.DataFrame:
        """加载Excel文件"""
        print(f"[1/4] 加载Excel文件: {self.excel_path}")
        if not os.path.exists(self.excel_path):
            raise FileNotFoundError(f"Excel文件不存在: {self.excel_path}")

        # 读取Excel,排除最后一列(运动轨迹)
        df = pd.read_excel(self.excel_path)
        print(f"   原始列: {df.columns.tolist()}")

        # 删除运动轨迹列
        if '运动轨迹' in df.columns:
            df = df.drop(columns=['运动轨迹'])
            print("   已删除'运动轨迹'列")

        print(f"   加载 {len(df)} 条记录")
        return df

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """数据清洗"""
        print("[2/4] 数据清洗中...")

        # 处理NaN值
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

        print(f"   清洗完成, 有效记录: {len(df)}")
        return df

    def create_table_if_not_exists(self, conn):
        """如果表不存在则创建"""
        print("[3/4] 检查数据库表...")
        with conn.cursor() as cursor:
            # 检查表是否存在
            cursor.execute("SHOW TABLES LIKE 'training_records'")
            result = cursor.fetchone()

            if not result:
                print("   表不存在,正在创建training_records表...")
                # 读取SQL文件
                sql_file = project_root / "scripts/training_tables.sql"
                if not sql_file.exists():
                    raise FileNotFoundError(f"SQL文件不存在: {sql_file}")

                with open(sql_file, 'r', encoding='utf-8') as f:
                    sql_script = f.read()

                # 分割并执行SQL语句
                for statement in sql_script.split(';'):
                    statement = statement.strip()
                    if statement and not statement.startswith('--'):
                        try:
                            cursor.execute(statement)
                        except pymysql.Error as e:
                            # 忽略视图创建错误(可能已存在)
                            if 'CREATE OR REPLACE VIEW' not in statement:
                                print(f"   警告: SQL执行失败 - {e}")

                conn.commit()
                print("   表创建成功!")
            else:
                print("   表已存在,跳过创建")

    def import_to_db(self, df: pd.DataFrame):
        """导入数据到数据库"""
        print("[4/4] 导入数据到数据库...")

        conn = pymysql.connect(**self.db_config)
        try:
            # 创建表(如果不存在)
            self.create_table_if_not_exists(conn)

            # 准备插入语句
            insert_sql = """
                INSERT IGNORE INTO training_records (
                    user_id, exercise_type, duration_seconds, start_time, end_time,
                    calories, distance_meters, avg_heart_rate, max_heart_rate,
                    heart_rate_data, add_ts, last_modify_ts, data_source
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """

            now_ts = int(datetime.now().timestamp())
            success_count = 0
            failed_count = 0

            with conn.cursor() as cursor:
                for idx, row in df.iterrows():
                    try:
                        values = (
                            'default_user',  # user_id
                            row['运动类型'],
                            int(row['运动时长(秒)']),
                            row['开始时间'],
                            row['结束时间'],
                            int(row['卡路里']) if row['卡路里'] else None,
                            float(row['运动距离(米)']) if row['运动距离(米)'] else None,
                            int(row['平均心率']) if row['平均心率'] else None,
                            int(row['最大心率']) if row['最大心率'] else None,
                            str(row['心率记录']) if row['心率记录'] else '[]',
                            now_ts,
                            now_ts,
                            'excel_import'
                        )
                        cursor.execute(insert_sql, values)
                        success_count += 1

                        if (idx + 1) % 100 == 0:
                            print(f"   已处理 {idx + 1}/{len(df)} 条记录...")

                    except Exception as e:
                        failed_count += 1
                        print(f"   第{idx+1}行导入失败: {e}")

                conn.commit()

            print(f"\n导入完成!")
            print(f"   成功: {success_count} 条")
            print(f"   失败: {failed_count} 条")

        finally:
            conn.close()

    def run(self):
        """执行完整导入流程"""
        print("="*80)
        print("训练数据导入工具")
        print("="*80)

        try:
            # 加载Excel
            df = self.load_excel()

            # 清洗数据
            df = self.clean_data(df)

            # 导入数据库
            self.import_to_db(df)

            print("\n✅ 导入成功!")

        except Exception as e:
            print(f"\n❌ 导入失败: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

def main():
    """主函数"""
    # Excel文件路径
    excel_path = "/home/dzs-ai-4/dzs-dev/Agent/multiRunningAgents/data/406099.xlsx"

    # 检查文件是否存在
    if not excel_path.exists():
        print(f"错误: Excel文件不存在 - {excel_path}")
        print("请将406099.xlsx文件放在项目根目录下")
        sys.exit(1)

    # 执行导入
    importer = TrainingDataImporter(str(excel_path))
    importer.run()

if __name__ == "__main__":
    main()
