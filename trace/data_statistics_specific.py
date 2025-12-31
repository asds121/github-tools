#!/usr/bin/env python3
"""数据统计 - 特定功能模块"""
from datetime import datetime, timedelta


def get_today_stats(records):
    """获取今日统计数据"""
    today = datetime.now().date()
    today_records = [record for record in records if datetime.fromisoformat(record["timestamp"]).date() == today]
    return today_records


def get_weekly_stats(records):
    """获取本周统计数据"""
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    weekly_records = [record for record in records if week_start <= datetime.fromisoformat(record["timestamp"]).date() <= today]
    return weekly_records


def get_monthly_stats(records):
    """获取本月统计数据"""
    today = datetime.now().date()
    month_start = today.replace(day=1)
    monthly_records = [record for record in records if month_start <= datetime.fromisoformat(record["timestamp"]).date() <= today]
    return monthly_records


def get_ip_usage_distribution(records):
    """获取IP使用分布"""
    if not records:
        return {}
    
    ip_distribution = {}
    total = len(records)
    
    for record in records:
        if "ip" in record:
            ip = record["ip"]
            if ip not in ip_distribution:
                ip_distribution[ip] = 0
            ip_distribution[ip] += 1
    
    # 转换为百分比
    for ip in ip_distribution:
        ip_distribution[ip] = round((ip_distribution[ip] / total) * 100, 2)
    
    return dict(sorted(ip_distribution.items(), key=lambda x: x[1], reverse=True))
