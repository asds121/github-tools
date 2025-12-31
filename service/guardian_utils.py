#!/usr/bin/env python3
"""GitHub守护进程 - 工具函数模块"""
import os
import time
import socket
import threading
import json
from .config_utils import get_state_file_path, get_hosts_path

# 引入trace层模块，符合service层必须引用trace层内容的要求
from trace import hosts_manager
from trace import connection_diagnostic


# 状态锁
state_lock = threading.Lock()


def save_state(state):
    """保存状态到文件"""
    state_file = get_state_file_path()
    with state_lock:
        try:
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False)
        except Exception:
            pass


def load_state():
    """加载上次状态"""
    state_file = get_state_file_path()
    try:
        if state_file.exists():
            with open(state_file, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return None


def is_admin():
    """检查是否具有管理员权限"""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def test_connect(ip, timeout=3):
    """测试IP连接是否可达"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((ip, 443))
        s.close()
        return True
    except Exception:
        return False


def find_best_ip(ip_pool, timeout=3):
    """查找最佳的可用IP"""
    for ip in ip_pool:
        if test_connect(ip, timeout=timeout):
            return ip
    return None


def check_connection(ip_pool, timeout=3):
    """检查GitHub连接状态"""
    for ip in ip_pool:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((ip, 443))
            sock.close()
            return True
        except Exception:
            continue
    return False


def get_current_hosts_github_ip():
    """获取当前hosts中github.com的IP"""
    hosts_path = get_hosts_path()
    try:
        with open(hosts_path, "rb") as f:
            content = f.read().decode("gbk", errors="ignore")
        for line in content.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) >= 2 and parts[1] == "github.com":
                return parts[0]
    except Exception:
        pass
    return None


def update_hosts(ip, domains=None):
    """更新hosts文件"""
    hosts_path = get_hosts_path()
    if not ip:
        return {"success": False, "error": "未提供IP"}

    domains = domains or ["github.com", "api.github.com"]

    try:
        with open(hosts_path, "rb") as f:
            content = f.read().decode("gbk", errors="ignore")
        lines = [line for line in content.split("\n") if "github" not in line.lower() or "#" in line]
        for domain in domains:
            lines.append(f"{ip}    {domain}")
        with open(hosts_path, "wb") as f:
            f.write("\n".join(lines).encode("gbk"))
        os.system("ipconfig /flushdns")
        return {"success": True, "ip": ip}
    except Exception as e:
        return {"success": False, "error": str(e)}
