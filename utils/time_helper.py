# -*- coding: utf-8 -*-
"""
时间工具模块
提供动态时间注入功能,确保LLM在搜索时使用当前时间
"""

from datetime import datetime
from zoneinfo import ZoneInfo


def get_current_time_context() -> str:
    """
    获取当前时间上下文信息,用于注入到提示词中

    Returns:
        格式化的当前时间信息字符串
    """
    # 使用北京时区
    beijing_tz = ZoneInfo("Asia/Shanghai")
    now = datetime.now(beijing_tz)

    # 格式化时间信息
    current_date = now.strftime("%Y年%m月%d日")
    current_time = now.strftime("%H:%M")
    weekday_map = {
        0: "周一", 1: "周二", 2: "周三", 3: "周四",
        4: "周五", 5: "周六", 6: "周日"
    }
    weekday = weekday_map[now.weekday()]

    # 组合时间上下文
    time_context = f"""
**当前时间信息**:
- 日期: {current_date} ({weekday})
- 时刻: {current_time}
- 时区: 北京时间 (UTC+8)

**搜索时间要求**:
⚠️ **重要**: 你的训练数据可能已经过期,请务必在搜索时带上时间信息!
- 查询最新资讯时,使用 "{now.year}年" 或 "最新" 等时间关键词
- 查询比赛信息时,明确指定年份 "2025年XX马拉松" 而不是 "XX马拉松"
- 查询装备价格时,使用 "当前价格" 或 "{now.year}年价格"
- 查询天气预报时,使用具体日期 "{current_date}" 或 "明天/后天"

示例:
- ❌ 错误: "北京马拉松报名时间" (可能搜到2023年的旧信息)
- ✅ 正确: "2025年北京马拉松报名时间"
- ❌ 错误: "Nike Vaporfly价格" (可能搜到过期价格)
- ✅ 正确: "Nike Vaporfly 2025年最新价格"
"""

    return time_context


def get_date_for_search() -> str:
    """
    获取用于搜索的日期字符串 (YYYY-MM-DD格式)

    Returns:
        格式化的日期字符串
    """
    beijing_tz = ZoneInfo("Asia/Shanghai")
    now = datetime.now(beijing_tz)
    return now.strftime("%Y-%m-%d")


def get_year_for_search() -> str:
    """
    获取当前年份字符串,用于搜索关键词

    Returns:
        当前年份字符串
    """
    beijing_tz = ZoneInfo("Asia/Shanghai")
    now = datetime.now(beijing_tz)
    return str(now.year)


def inject_time_into_prompt(prompt: str) -> str:
    """
    将当前时间信息注入到提示词中

    Args:
        prompt: 原始提示词

    Returns:
        注入时间信息后的提示词
    """
    time_context = get_current_time_context()

    # 在提示词开头注入时间信息
    enhanced_prompt = f"""{time_context}

---

{prompt}"""

    return enhanced_prompt


if __name__ == "__main__":
    # 测试函数
    print("=== 测试时间上下文 ===")
    print(get_current_time_context())

    print("\n=== 测试搜索日期 ===")
    print(f"搜索日期: {get_date_for_search()}")

    print("\n=== 测试搜索年份 ===")
    print(f"搜索年份: {get_year_for_search()}")

    print("\n=== 测试提示词注入 ===")
    test_prompt = "你是一个跑步助手,请帮我搜索相关信息。"
    print(inject_time_into_prompt(test_prompt))
