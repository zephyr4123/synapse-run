#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫数据库监控脚本
实时监控MediaCrawler爬虫数据的增长情况
"""

import pymysql
import time
import os
from datetime import datetime
from collections import defaultdict

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'huangsuxiang',
    'password': 'Wodeshijie1.12',
    'database': 'running',
    'charset': 'utf8mb4'
}

# 平台与表的映射关系
PLATFORM_TABLES = {
    'bilibili': {
        'video': 'bilibili_video',
        'comment': 'bilibili_video_comment'
    },
    'kuaishou': {
        'video': 'kuaishou_video',
        'comment': 'kuaishou_video_comment'
    },
    'douyin': {
        'video': 'douyin_aweme',
        'comment': 'douyin_aweme_comment'
    },
    'xiaohongshu': {
        'note': 'xhs_note',
        'comment': 'xhs_note_comment'
    },
    'weibo': {
        'note': 'weibo_note',
        'comment': 'weibo_note_comment'
    },
    'tieba': {
        'note': 'tieba_note',
        'comment': 'tieba_comment'
    },
    'zhihu': {
        'note': 'zhihu_note',
        'comment': 'zhihu_comment'
    }
}


class CrawlerDataMonitor:
    def __init__(self):
        self.conn = None
        self.previous_counts = {}

    def connect_db(self):
        """连接数据库"""
        try:
            self.conn = pymysql.connect(**DB_CONFIG)
            return True
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            return False

    def close_db(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()

    def get_table_count(self, table_name):
        """获取表的行数"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                return cursor.fetchone()[0]
        except Exception as e:
            # print(f"查询表 {table_name} 失败: {e}")
            return 0

    def get_latest_records(self, table_name, limit=5):
        """获取最新的几条记录"""
        try:
            with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
                # 根据不同表选择不同的字段
                if 'video' in table_name or 'aweme' in table_name:
                    time_field = 'create_time'
                    title_field = 'title'
                elif 'note' in table_name:
                    time_field = 'create_time'
                    title_field = 'title' if table_name != 'weibo_note' else 'content'
                elif 'comment' in table_name:
                    time_field = 'create_time'
                    title_field = 'content'
                else:
                    return []

                sql = f"""
                SELECT {title_field}, {time_field}
                FROM {table_name}
                ORDER BY id DESC
                LIMIT {limit}
                """
                cursor.execute(sql)
                return cursor.fetchall()
        except Exception as e:
            # print(f"查询表 {table_name} 最新记录失败: {e}")
            return []

    def get_today_count(self, table_name):
        """获取今天新增的数据量"""
        try:
            with self.conn.cursor() as cursor:
                # 获取今天的开始时间戳 (00:00:00)
                today_start = int(datetime.now().replace(
                    hour=0, minute=0, second=0, microsecond=0
                ).timestamp())

                sql = f"""
                SELECT COUNT(*) FROM {table_name}
                WHERE create_time >= {today_start}
                """
                cursor.execute(sql)
                return cursor.fetchone()[0]
        except Exception as e:
            return 0

    def display_statistics(self):
        """显示统计信息"""
        current_counts = {}

        # 清屏
        os.system('clear' if os.name != 'nt' else 'cls')

        # 打印标题
        print("=" * 80)
        print(f"{'MediaCrawler 数据监控面板':^80}")
        print(f"{'更新时间: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'):^80}")
        print("=" * 80)
        print()

        # 统计总数
        total_posts = 0
        total_comments = 0

        for platform, tables in PLATFORM_TABLES.items():
            platform_display = {
                'bilibili': 'B站',
                'kuaishou': '快手',
                'douyin': '抖音',
                'xiaohongshu': '小红书',
                'weibo': '微博',
                'tieba': '贴吧',
                'zhihu': '知乎'
            }

            print(f"📊 {platform_display[platform]}")
            print("-" * 80)

            for content_type, table_name in tables.items():
                count = self.get_table_count(table_name)
                today_count = self.get_today_count(table_name)
                current_counts[table_name] = count

                # 计算增量
                delta = 0
                if table_name in self.previous_counts:
                    delta = count - self.previous_counts[table_name]

                # 累计统计
                if content_type in ['video', 'note']:
                    total_posts += count
                else:
                    total_comments += count

                # 显示颜色标记
                status_icon = "🔴" if count == 0 else "🟢"
                delta_str = ""
                if delta > 0:
                    delta_str = f" (+{delta} 本轮新增)"
                elif delta < 0:
                    delta_str = f" ({delta} 减少)"

                content_type_cn = {
                    'video': '视频',
                    'note': '笔记',
                    'comment': '评论'
                }

                print(f"  {status_icon} {content_type_cn.get(content_type, content_type):6} | "
                      f"总量: {count:6} | 今日: {today_count:5}{delta_str}")

                # 显示最新记录
                if count > 0 and delta > 0:
                    latest = self.get_latest_records(table_name, limit=1)
                    if latest:
                        record = latest[0]
                        title_key = list(record.keys())[0]
                        title = record[title_key]
                        if title:
                            title = title[:50] + "..." if len(title) > 50 else title
                            print(f"     └─ 最新: {title}")

            print()

        # 显示总览
        print("=" * 80)
        print(f"📈 总览统计")
        print("-" * 80)
        print(f"  • 内容总量 (视频/笔记): {total_posts:,}")
        print(f"  • 评论总量: {total_comments:,}")
        print(f"  • 数据总量: {total_posts + total_comments:,}")
        print("=" * 80)

        # 更新历史计数
        self.previous_counts = current_counts

    def monitor_loop(self, interval=5):
        """监控循环"""
        print("🚀 启动爬虫数据监控...")
        print(f"⏱️  刷新间隔: {interval} 秒")
        print("⌨️  按 Ctrl+C 退出监控")
        time.sleep(2)

        try:
            while True:
                self.display_statistics()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n\n✅ 监控已停止")

    def show_single_snapshot(self):
        """显示单次快照"""
        self.display_statistics()


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='MediaCrawler 数据监控脚本')
    parser.add_argument('-i', '--interval', type=int, default=5,
                        help='刷新间隔(秒),默认5秒')
    parser.add_argument('-o', '--once', action='store_true',
                        help='只显示一次,不循环监控')

    args = parser.parse_args()

    monitor = CrawlerDataMonitor()

    if not monitor.connect_db():
        return

    try:
        if args.once:
            monitor.show_single_snapshot()
        else:
            monitor.monitor_loop(interval=args.interval)
    finally:
        monitor.close_db()


if __name__ == '__main__':
    main()
