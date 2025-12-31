#!/usr/bin/env python3
"""定时巡检 - 辅助工具模块"""
import json
from pathlib import Path
from datetime import datetime, timedelta


def load_config(config_path):
    """加载配置"""
    if config_path.exists():
        try:
            return json.loads(config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}


def save_config(config, config_path):
    """保存配置"""
    config_path.write_text(json.dumps(config, indent=4, ensure_ascii=False), encoding="utf-8")


def load_history(history_path):
    """加载历史记录"""
    if history_path.exists():
        try:
            return json.loads(history_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []
    return []


def save_history(history, history_path):
    """保存历史记录"""
    history_path.write_text(json.dumps(history, indent=4, ensure_ascii=False), encoding="utf-8")


def prune_history(history, retention_days):
    """清理过期历史记录"""
    cutoff_date = datetime.now() - timedelta(days=retention_days)
    return [record for record in history if datetime.fromisoformat(record["timestamp"]) >= cutoff_date]


def generate_alert(message, alert_method):
    """生成告警"""
    if alert_method == "console":
        print(f"[告警] {message}")
    # 这里可以扩展其他告警方式，比如邮件、弹窗等


def check_ip_blacklist(ip, blacklist_path):
    """检查IP是否在黑名单中"""
    if blacklist_path.exists():
        try:
            blacklist = json.loads(blacklist_path.read_text(encoding="utf-8"))
            return ip in blacklist.get("blacklist", [])
        except (json.JSONDecodeError, AttributeError):
            return False
    return False


def update_ip_blacklist(ip, blacklist_path, reason="自动加入黑名单"):
    """更新IP黑名单"""
    if blacklist_path.exists():
        try:
            blacklist = json.loads(blacklist_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            blacklist = {"blacklist": [], "reasons": {}}
    else:
        blacklist = {"blacklist": [], "reasons": {}}
    
    if ip not in blacklist["blacklist"]:
        blacklist["blacklist"].append(ip)
        blacklist["reasons"][ip] = {
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
        blacklist_path.write_text(json.dumps(blacklist, indent=4, ensure_ascii=False), encoding="utf-8")
        return True
    return False
