import datetime


def get_current_quarter_date_range():
    """获取当前季度的开始日期和结束日期"""
    today = datetime.date.today()
    year = today.year
    # 确定当前季度
    quarter = (today.month - 1) // 3 + 1  # 1-4季度
    # 计算季度开始月份和结束月份
    start_month = (quarter - 1) * 3 + 1
    end_month = quarter * 3
    # 构造季度开始日期（当月1日）和结束日期（当月最后一天）
    quarter_start = datetime.date(year, start_month, 1)
    # 计算结束月份的最后一天：下一个月1日减1天
    if end_month == 12:
        quarter_end = datetime.date(year, 12, 31)
    else:
        quarter_end = datetime.date(year, end_month + 1, 1) - datetime.timedelta(days=1)
    return quarter_start, quarter_end


def calculate_quarter_weeks():
    """计算当前季度的周信息：总周数、各周起止日期、当前日期在季度的第几周"""
    # 1. 获取当前季度起止日期
    quarter_start, quarter_end = get_current_quarter_date_range()
    today = datetime.date.today()

    # 2. 计算季度内所有日期的ISO周（年+周数，避免跨年份问题，如Q1可能包含上一年的最后一周）
    quarter_week_set = set()
    # 遍历季度内所有日期，提取唯一的(年, 周数)组合
    delta = datetime.timedelta(days=1)
    current_date = quarter_start
    while current_date <= quarter_end:
        iso_year, iso_week, _ = current_date.isocalendar()
        quarter_week_set.add((iso_year, iso_week))
        current_date += delta

    # 3. 排序周信息，得到有序的周列表
    sorted_quarter_weeks = sorted(list(quarter_week_set))
    total_weeks = len(sorted_quarter_weeks)  # 季度总周数

    # 4. 计算每个周的起止日期（周一到周日）
    week_date_ranges = []
    for iso_y, iso_w in sorted_quarter_weeks:
        # 计算该周的周一（ISO周的第一天）
        # 先取该年第1周的周一，再偏移对应周数
        first_day_of_year = datetime.date(iso_y, 1, 1)
        # 找到该年第1周的周一
        while first_day_of_year.isocalendar()[1] != 1 or first_day_of_year.weekday() != 0:
            first_day_of_year -= datetime.timedelta(days=1)
        # 偏移到目标周的周一
        week_monday = first_day_of_year + datetime.timedelta(weeks=iso_w - 1)
        # 周日是周一+6天
        week_sunday = week_monday + datetime.timedelta(days=6)
        week_date_ranges.append({
            "iso_year": iso_y,
            "iso_week": iso_w,
            "week_monday": week_monday,
            "week_sunday": week_sunday
        })

    # 5. 计算当前日期属于当前季度的第几周（从1开始计数）
    today_iso_year, today_iso_week, _ = today.isocalendar()
    today_quarter_week_index = None
    for idx, (iso_y, iso_w) in enumerate(sorted_quarter_weeks, 1):
        if iso_y == today_iso_year and iso_w == today_iso_week:
            today_quarter_week_index = idx
            break

    # 6. 整理返回结果
    result = {
        "current_quarter": (today.month - 1) // 3 + 1,
        "quarter_year": today.year,
        "quarter_start": quarter_start,
        "quarter_end": quarter_end,
        "total_weeks_in_quarter": total_weeks,
        "today_quarter_week": today_quarter_week_index,
        "quarter_weeks_detail": week_date_ranges
    }
    return result


# 调用函数并打印结果
if __name__ == "__main__":
    quarter_week_info = calculate_quarter_weeks()
    # 打印核心信息
    print(f"当前年份：{quarter_week_info['quarter_year']}")
    print(f"当前季度：Q{quarter_week_info['current_quarter']}")
    print(f"季度起止日期：{quarter_week_info['quarter_start']} ~ {quarter_week_info['quarter_end']}")
    print(f"当前季度总周数：{quarter_week_info['total_weeks_in_quarter']} 周")
    print(f"当前日期属于本季度第 {quarter_week_info['today_quarter_week']} 周")

    # 打印所有周的详细起止日期
    print("\n本季度各周起止日期（周一~周日）：")
    for idx, week in enumerate(quarter_week_info['quarter_weeks_detail'], 1):
        print(
            f"第{idx}周：{week['week_monday']} ~ {week['week_sunday']}（ISO {week['iso_year']} 年第{week['iso_week']}周）")
