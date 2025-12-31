#!/usr/bin/env python3
"""数据统计 - 工具模块"""
import json
from pathlib import Path
from datetime import datetime


def load_inspection_history(file_path):
    """加载巡检历史数据"""
    if file_path.exists():
        try:
            return json.loads(file_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return []


def load_ip_quality_db(file_path):
    """加载 IP 质量数据库"""
    if file_path.exists():
        try:
            return json.loads(file_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def save_inspection_history(data, file_path):
    """保存巡检历史数据"""
    try:
        file_path.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")
        return True
    except Exception:
        return False


def save_ip_quality_db(data, file_path):
    """保存 IP 质量数据库"""
    try:
        file_path.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")
        return True
    except Exception:
        return False


def get_records_by_date_range(records, start_date, end_date):
    """获取指定日期范围内的记录"""
    return [
        record for record in records
        if start_date <= datetime.fromisoformat(record["timestamp"]).date() <= end_date
    ]


def group_records_by_period(records, period="day"):
    """按指定周期分组记录"""
    grouped = {}
    for record in records:
        dt = datetime.fromisoformat(record["timestamp"])
        if period == "day":
            key = dt.strftime("%Y-%m-%d")
        elif period == "hour":
            key = dt.strftime("%Y-%m-%d %H")
        else:
            key = dt.strftime("%Y-%m-%d")
        
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(record)
    return grouped
