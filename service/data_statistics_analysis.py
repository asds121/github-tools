#!/usr/bin/env python3
"""数据统计 - 分析模块"""
from datetime import datetime, timedelta

# 引入trace层模块，符合service层必须引用trace层内容的要求
from trace import data_statistics
from trace import connection_diagnostic
from collections import defaultdict


def calculate_daily_stats(records):
    """计算每日统计数据"""
    if not records:
        return {
            "count": 0,
            "normal": 0,
            "abnormal": 0,
            "avg_latency": 0,
            "availability": 0
        }
    
    normal_count = sum(1 for r in records if r["status"] != "bad")
    abnormal_count = len(records) - normal_count
    
    # 计算平均延迟（只包含正常记录）
    normal_latencies = [r["latency"] for r in records if r["status"] != "bad"]
    avg_latency = sum(normal_latencies) / len(normal_latencies) if normal_latencies else 0
    
    # 计算可用率
    availability = (normal_count / len(records)) * 100 if records else 0
    
    return {
        "count": len(records),
        "normal": normal_count,
        "abnormal": abnormal_count,
        "avg_latency": round(avg_latency, 1),
        "availability": round(availability, 1)
    }


def calculate_trend_stats(records, days=7):
    """计算趋势统计数据"""
    # 按天分组记录
    daily_records = {}
    for record in records:
        date = datetime.fromisoformat(record["timestamp"]).strftime("%Y-%m-%d")
        if date not in daily_records:
            daily_records[date] = []
        daily_records[date].append(record)
    
    # 生成最近N天的日期列表
    trend_dates = []
    today = datetime.now().date()
    for i in range(days):
        date = today - timedelta(days=i)
        trend_dates.append(date.strftime("%Y-%m-%d"))
    trend_dates.reverse()  # 按时间顺序排列
    
    # 计算每天的统计数据
    trend_data = []
    for date in trend_dates:
        day_records = daily_records.get(date, [])
        day_stats = calculate_daily_stats(day_records)
        trend_data.append({
            "date": date,
            **day_stats
        })
    
    return trend_data


def calculate_hourly_stats(records):
    """计算每小时统计数据"""
    hourly_records = {}
    for record in records:
        hour_key = datetime.fromisoformat(record["timestamp"]).strftime("%H")
        if hour_key not in hourly_records:
            hourly_records[hour_key] = []
        hourly_records[hour_key].append(record)
    
    hourly_stats = []
    for hour in range(24):
        hour_str = f"{hour:02d}"
        hour_records = hourly_records.get(hour_str, [])
        stats = calculate_daily_stats(hour_records)
        hourly_stats.append({
            "hour": hour_str,
            **stats
        })
    
    return hourly_stats


def calculate_weekly_stats(records):
    """计算每周统计数据"""
    weekly_records = defaultdict(list)
    for record in records:
        dt = datetime.fromisoformat(record["timestamp"])
        # 获取周数（每年的第几周）
        week_num = dt.isocalendar()[1]
        year_week = f"{dt.year}-W{week_num:02d}"
        weekly_records[year_week].append(record)
    
    weekly_stats = []
    for week, week_records in sorted(weekly_records.items()):
        stats = calculate_daily_stats(week_records)
        weekly_stats.append({
            "week": week,
            **stats
        })
    
    return weekly_stats


def analyze_latency_distribution(records):
    """分析延迟分布"""
    # 只包含正常记录的延迟数据
    latencies = [r["latency"] for r in records if r["status"] != "bad" and r["latency"] > 0]
    if not latencies:
        return {
            "bins": [],
            "counts": []
        }
    
    # 定义延迟区间
    bins = [0, 50, 100, 200, 500, 1000, float("inf")]
    bin_labels = ["0-50ms", "50-100ms", "100-200ms", "200-500ms", "500-1000ms", "1000ms+"]
    
    # 统计每个区间的数量
    counts = [0] * len(bin_labels)
    for latency in latencies:
        for i, (lower, upper) in enumerate(zip(bins[:-1], bins[1:])):
            if lower <= latency < upper:
                counts[i] += 1
                break
    
    return {
        "bins": bin_labels,
        "counts": counts
    }


def get_top_abnormal_ips(ip_quality_db, limit=10):
    """获取异常IP排行榜"""
    if not ip_quality_db:
        return []
    
    # 按失败次数排序
    sorted_ips = sorted(
        ip_quality_db.items(),
        key=lambda x: x[1].get("fail_count", 0),
        reverse=True
    )
    
    # 提取前N个
    top_ips = []
    for ip, data in sorted_ips[:limit]:
        top_ips.append({
            "ip": ip,
            "fail_count": data.get("fail_count", 0),
            "last_fail_time": data.get("last_fail_time", ""),
            "avg_latency": data.get("avg_latency", 0)
        })
    
    return top_ips
