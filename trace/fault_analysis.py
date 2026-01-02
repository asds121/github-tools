#!/usr/bin/env python3
"""故障分析 - 基础日志记录和数据存储"""
import json
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "trace" / "data"
DATA_DIR.mkdir(exist_ok=True)

# 故障记录文件路径
FAULT_HISTORY = DATA_DIR / "fault_history.json"
REPAIR_HISTORY = DATA_DIR / "repair_history.json"

# 故障类型定义
FAULT_TYPES = {
    "dns_failure": "DNS解析失败",
    "tcp_failure": "TCP连接失败",
    "http_failure": "HTTP响应失败",
    "ssl_failure": "SSL证书错误",
    "timeout": "连接超时",
    "other": "其他故障"
}

# 修复方案定义
REPAIR_SCHEMES = {
    "hosts_update": "更新Hosts文件",
    "dns_change": "更换DNS服务器",
    "ip_switch": "切换IP地址",
    "proxy_use": "使用代理",
    "restart_network": "重启网络",
    "other": "其他修复方案"
}


def load_fault_history():
    """加载故障历史记录"""
    if FAULT_HISTORY.exists():
        try:
            with open(FAULT_HISTORY, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []



def save_fault_history(history):
    """保存故障历史记录"""
    with open(FAULT_HISTORY, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)



def load_repair_history():
    """加载修复历史记录"""
    if REPAIR_HISTORY.exists():
        try:
            with open(REPAIR_HISTORY, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []



def save_repair_history(history):
    """保存修复历史记录"""
    with open(REPAIR_HISTORY, "w", encoding="utf-8-sig") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)



def log_fault(fault_type, details=None, latency=None):
    """记录故障信息"""
    fault_record = {
        "timestamp": datetime.now().isoformat(),
        "fault_type": fault_type,
        "fault_name": FAULT_TYPES.get(fault_type, "未知故障"),
        "details": details or {},
        "latency": latency
    }
    
    history = load_fault_history()
    history.append(fault_record)
    save_fault_history(history)
    return fault_record



def log_repair(scheme, success, fault_type=None, details=None):
    """记录修复信息"""
    repair_record = {
        "timestamp": datetime.now().isoformat(),
        "scheme": scheme,
        "scheme_name": REPAIR_SCHEMES.get(scheme, "未知修复方案"),
        "success": success,
        "fault_type": fault_type,
        "details": details or {},
        "reason": details.get("reason", "未明确"),
        "fix_method": details.get("fix_method", "未记录"),
        "verification": details.get("verification", "未验证")
    }
    
    history = load_repair_history()
    history.append(repair_record)
    save_repair_history(history)
    return repair_record


def run():
    """运行基础故障分析功能"""
    print("故障分析基础服务已启动")
    return {
        "success": True,
        "message": "故障分析基础服务运行正常",
        "available_functions": [
            "log_fault - 记录故障信息",
            "log_repair - 记录修复信息",
            "load_fault_history - 加载故障历史",
            "load_repair_history - 加载修复历史"
        ]
    }


if __name__ == "__main__":
    run()
