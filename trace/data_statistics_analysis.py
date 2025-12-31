#!/usr/bin/env python3
"""数据统计 - 分析模块"""
from datetime import datetime, timedelta
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
    
    # 计算每天的统计数据
    trend = []
    for date in sorted(daily_records.keys()):
        stats = calculate_daily_stats(daily_records[date])
        trend.append({
            "date": date,
            "stats": stats
        })
    
    return trend[-days:]  # 返回最近几天的数据


def calculate_hourly_stats(records):
    """计算每小时统计数据"""
    # 按小时分组记录
    hourly_records = {}
    for record in records:
        hour = datetime.fromisoformat(record["timestamp"]).strftime("%Y-%m-%d %H")
        if hour not in hourly_records:
            hourly_records[hour] = []
        hourly_records[hour].append(record)
    
    # 计算每小时的统计数据
    hourly_stats = []
    for hour in sorted(hourly_records.keys()):
        stats = calculate_daily_stats(hourly_records[hour])
        hourly_stats.append({
            "hour": hour,
            "stats": stats
        })
    
    return hourly_stats


def calculate_weekly_stats(records):
    """计算每周统计数据"""
    # 按周分组记录
    weekly_records = {}
    for record in records:
        dt = datetime.fromisoformat(record["timestamp"])
        year, week, _ = dt.isocalendar()
        key = f"{year}-W{week:02d}"
        if key not in weekly_records:
            weekly_records[key] = []
        weekly_records[key].append(record)
    
    # 计算每周的统计数据
    weekly_stats = []
    for week in sorted(weekly_records.keys()):
        stats = calculate_daily_stats(weekly_records[week])
        weekly_stats.append({
            "week": week,
            "stats": stats
        })
    
    return weekly_stats


def analyze_latency_distribution(records):
    """分析延迟分布"""
    if not records:
        return {
            "<100ms": 0,
            "100-200ms": 0,
            "200-300ms": 0,
            ">300ms": 0
        }
    
    distribution = {
        "<100ms": 0,
        "100-200ms": 0,
        "200-300ms": 0,
        ">300ms": 0
    }
    
    for record in records:
        if record["status"] != "bad":
            latency = record["latency"]
            if latency < 100:
                distribution["<100ms"] += 1
            elif 100 <= latency < 200:
                distribution["100-200ms"] += 1
            elif 200 <= latency < 300:
                distribution["200-300ms"] += 1
            else:
                distribution[">300ms"] += 1
    
    return distribution


def get_top_abnormal_ips(records, top_n=5):
    """获取异常次数最多的IP"""
    if not records:
        return []
    
    ip_abnormal_count = defaultdict(int)
    for record in records:
        if record["status"] == "bad" and "ip" in record:
            ip_abnormal_count[record["ip"]] += 1
    
    # 排序并返回前N个
    sorted_ips = sorted(ip_abnormal_count.items(), key=lambda x: x[1], reverse=True)
    return [{"ip": ip, "count": count} for ip, count in sorted_ips[:top_n]]
