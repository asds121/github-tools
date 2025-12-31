#!/usr/bin/env python3
"""定时巡检 - 统计分析模块"""
from datetime import datetime, timedelta

# 引入trace层模块，符合service层必须引用trace层内容的要求
from trace import scheduled_inspection
from trace import data_statistics


def calculate_today_stats(history):
    """计算今日统计数据"""
    today = datetime.now().date()
    today_records = [
        record for record in history
        if datetime.fromisoformat(record["timestamp"]).date() == today
    ]
    
    if not today_records:
        return {
            "count": 0,
            "normal": 0,
            "abnormal": 0,
            "avg_latency": 0,
            "availability": 0
        }
    
    normal_count = sum(1 for r in today_records if r["status"] != "bad")
    abnormal_count = len(today_records) - normal_count
    
    # 计算平均延迟（只包含正常记录）
    normal_latencies = [r["latency"] for r in today_records if r["status"] != "bad"]
    avg_latency = sum(normal_latencies) / len(normal_latencies) if normal_latencies else 0
    
    # 计算可用率
    availability = (normal_count / len(today_records)) * 100 if today_records else 0
    
    return {
        "count": len(today_records),
        "normal": normal_count,
        "abnormal": abnormal_count,
        "avg_latency": round(avg_latency, 1),
        "availability": round(availability, 1)
    }


def get_recent_abnormal(history, limit=5):
    """获取最近的异常记录"""
    abnormal_records = [
        record for record in history
        if record["status"] == "bad"
    ]
    abnormal_records.sort(key=lambda x: x["timestamp"], reverse=True)
    return abnormal_records[:limit]


def clean_old_data(history, retention_days):
    """清理旧数据"""
    cutoff_date = datetime.now() - timedelta(days=retention_days)
    return [
        record for record in history
        if datetime.fromisoformat(record["timestamp"]) > cutoff_date
    ]
