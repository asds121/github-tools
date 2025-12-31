#!/usr/bin/env python3
"""数据统计 - 特定统计方法模块"""
from datetime import datetime, timedelta
from collections import defaultdict

# 引入trace层模块，符合service层必须引用trace层内容的要求
from trace import data_statistics


def get_today_stats(inspection_history):
    """获取今日统计数据"""
    today = datetime.now().date()
    today_records = [
        record for record in inspection_history
        if datetime.fromisoformat(record["timestamp"]).date() == today
    ]
    
    if not today_records:
        return {
            "test_count": 0,
            "success_rate": 0,
            "avg_latency": 0,
            "best_latency": 0,
            "worst_latency": 0,
            "best_ip": None
        }
    
    # 计算成功率
    success_count = sum(1 for r in today_records if r["status"] != "bad")
    success_rate = (success_count / len(today_records)) * 100
    
    # 计算延迟统计
    latencies = [r["latency"] for r in today_records if r["status"] != "bad"]
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    best_latency = min(latencies) if latencies else 0
    worst_latency = max(latencies) if latencies else 0
    
    return {
        "test_count": len(today_records),
        "success_rate": round(success_rate, 1),
        "avg_latency": round(avg_latency, 1),
        "best_latency": best_latency,
        "worst_latency": worst_latency,
        "best_ip": None  # 暂时未实现
    }


def get_weekly_stats(inspection_history):
    """获取本周统计数据"""
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_records = [
        record for record in inspection_history
        if week_start <= datetime.fromisoformat(record["timestamp"]).date() <= today
    ]
    
    if not week_records:
        return {
            "available_rate": 0,
            "avg_latency": 0,
            "best_time_period": None,
            "worst_time_period": None
        }
    
    # 计算可用率
    success_count = sum(1 for r in week_records if r["status"] != "bad")
    available_rate = (success_count / len(week_records)) * 100
    
    # 计算平均延迟
    latencies = [r["latency"] for r in week_records if r["status"] != "bad"]
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    
    # 计算最佳和最差时段
    hour_stats = defaultdict(list)
    for r in week_records:
        if r["status"] != "bad":
            hour = datetime.fromisoformat(r["timestamp"]).hour
            hour_stats[hour].append(r["latency"])
    
    # 计算每个小时的平均延迟
    hour_avg_latency = {}
    for hour, latency_list in hour_stats.items():
        hour_avg_latency[hour] = sum(latency_list) / len(latency_list)
    
    best_time = None
    worst_time = None
    if hour_avg_latency:
        best_time = min(hour_avg_latency.items(), key=lambda x: x[1])[0]
        worst_time = max(hour_avg_latency.items(), key=lambda x: x[1])[0]
    
    return {
        "available_rate": round(available_rate, 1),
        "avg_latency": round(avg_latency, 1),
        "best_time_period": f"{best_time:02d}:00-{best_time+1:02d}:00" if best_time is not None else None,
        "worst_time_period": f"{worst_time:02d}:00-{worst_time+1:02d}:00" if worst_time is not None else None
    }


def get_monthly_stats(inspection_history):
    """获取本月统计数据"""
    today = datetime.now().date()
    month_start = today.replace(day=1)
    month_records = [
        record for record in inspection_history
        if month_start <= datetime.fromisoformat(record["timestamp"]).date() <= today
    ]
    
    if not month_records:
        return {
            "available_rate": 0,
            "avg_latency": 0,
            "abnormal_days": 0
        }
    
    # 计算可用率
    success_count = sum(1 for r in month_records if r["status"] != "bad")
    available_rate = (success_count / len(month_records)) * 100
    
    # 计算平均延迟
    latencies = [r["latency"] for r in month_records if r["status"] != "bad"]
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    
    # 计算异常天数
    abnormal_days = set()
    for r in month_records:
        if r["status"] == "bad":
            abnormal_days.add(datetime.fromisoformat(r["timestamp"]).date())
    
    return {
        "available_rate": round(available_rate, 1),
        "avg_latency": round(avg_latency, 1),
        "abnormal_days": len(abnormal_days)
    }


def get_ip_usage_distribution(ip_quality_db):
    """获取 IP 使用分布"""
    # 这里简化处理，使用 IP 质量数据库中的数据
    if not ip_quality_db:
        return []
    
    # 计算每个 IP 的使用次数（基于成功次数）
    ip_usage = []
    for ip, data in ip_quality_db.items():
        success_count = data.get("success_count", 0)
        if success_count > 0:
            ip_usage.append({
                "ip": ip,
                "usage_count": success_count,
                "success_rate": round(data.get("success_count", 0) / max(data.get("count", 1), 1) * 100, 1)
            })
    
    # 按使用次数排序
    ip_usage.sort(key=lambda x: x["usage_count"], reverse=True)
    
    return ip_usage[:10]  # 返回前 10 个 IP
