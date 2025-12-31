#!/usr/bin/env python3
"""GitHub Hosts修复 - 修改hosts文件"""
import os
import sys
import json
import ctypes
from pathlib import Path

HOSTS_PATH = os.path.join(os.environ.get("SystemRoot", "C:\Windows"), "System32", "drivers", "etc", "hosts")

# 直接读取本地配置文件
CONFIG_PATH = Path(__file__).resolve().parent / "config.json"
if CONFIG_PATH.exists():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        CONFIG = json.load(f)
    GITHUB_IPS = CONFIG["github_ips"]
else:
    # 默认配置
    CONFIG = {"backup": True}
    GITHUB_IPS = {"github.com": "140.82.113.4", "api.github.com": "140.82.113.4"}

def is_admin():
    """检查是否具有管理员权限"""
    try:
        return os.getuid() == 0
    except AttributeError:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

def backup_hosts():
    """备份hosts文件"""
    try:
        with open(HOSTS_PATH, "rb") as f:
            with open(HOSTS_PATH + ".bak", "wb") as fw:
                fw.write(f.read())
        return True
    except Exception:
        return False

def update_hosts(github_ips=None, backup=None):
    """更新hosts文件"""
    github_ips = github_ips or GITHUB_IPS
    backup = backup if backup is not None else CONFIG.get("backup", True)

    if not is_admin():
        return {"success": False, "error": "需要管理员权限"}

    if backup:
        backup_hosts()

    try:
        with open(HOSTS_PATH, "rb") as f:
            content = f.read().decode("gbk", errors="ignore")
        lines = [line for line in content.split("\n") if "github" not in line.lower() or "#" in line]
        lines.extend([f"{v}    {k}" for k, v in github_ips.items()])
        with open(HOSTS_PATH, "wb") as f:
            f.write("\n".join(lines).encode("gbk"))
        os.system("ipconfig /flushdns")
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    result = update_hosts()
    return result

if __name__ == "__main__":
    main()
