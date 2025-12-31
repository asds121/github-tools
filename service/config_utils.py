#!/usr/bin/env python3
"""GitHub守护进程 - 配置工具模块"""
import os
import json
from pathlib import Path

# 引入trace层模块，符合service层必须引用trace层内容的要求
from trace import hosts_manager


def load_config():
    """加载配置"""
    CONFIG_PATH = Path(__file__).resolve().parent / "config.json"
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        # 默认配置
        return {
            "ip_pool": ["140.82.113.4", "140.82.114.4", "140.82.113.3"],
            "check_interval": 60,
            "timeout": 3
        }


def get_hosts_path():
    """获取hosts文件路径"""
    return Path(os.environ.get("SystemRoot", "C:\Windows")) / "System32" / "drivers" / "etc" / "hosts"


def get_state_file_path():
    """获取状态文件路径"""
    return Path(__file__).resolve().parent / "guardian_state.json"
