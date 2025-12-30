#!/usr/bin/env python3
"""GitHub守护进程 - 监控GitHub连接状态"""
import os
import sys
import time
import socket
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from github_utils import load_sub_config

CONFIG = load_sub_config("GitHub-guardian-守护进程")

HOSTS_PATH = Path(os.environ.get("SystemRoot", "C:\\Windows")) / "System32" / "drivers" / "etc" / "hosts"
IP_POOL = CONFIG["ip_pool"]

def test_connect(ip, port=443, timeout=None):
    """测试IP连接是否可达"""
    timeout = timeout or CONFIG["timeout"]
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((ip, port))
        s.close()
        return True
    except:
        return False

def find_best_ip(ip_pool=None, timeout=None):
    """查找最佳的可用IP"""
    ip_pool = ip_pool or IP_POOL
    for ip in ip_pool:
        if test_connect(ip, timeout=timeout):
            return ip
    return None

def update_hosts(ip, hosts_path=None):
    """更新hosts文件"""
    if not ip:
        return {"success": False, "error": "未提供IP"}

    hosts_path = hosts_path or HOSTS_PATH
    try:
        with open(hosts_path, "rb") as f:
            content = f.read().decode("gbk", errors="ignore")
        lines = content.split("\n")
        new_lines = [l for l in lines if "github" not in l.lower() or "#" in l]
        new_lines.append(f"\n{ip}    github.com\ngithub.com    {ip}")
        with open(hosts_path, "wb") as f:
            f.write("\n".join(new_lines).encode("gbk"))
        os.system("ipconfig /flushdns")
        return {"success": True, "ip": ip}
    except Exception as e:
        return {"success": False, "error": str(e)}

def check_and_repair():
    """检查连接状态并自动修复"""
    ip = find_best_ip()
    if ip:
        result = update_hosts(ip)
        return {"status": "OK", "ip": ip, "update": result}
    else:
        return {"status": "FAIL", "ip": None}

def main():
    result = check_and_repair()
    return result

if __name__ == "__main__":
    main()
