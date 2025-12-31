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
        # 支持多种编码格式读取hosts文件
        with open(HOSTS_PATH, "rb") as f:
            raw_content = f.read()
        
        # 尝试多种编码，提高兼容性
        content = None
        for encoding in ["utf-8", "gbk", "utf-16"]:
            try:
                content = raw_content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        
        if content is None:
            content = raw_content.decode("gbk", errors="ignore")
        
        # 移除所有github相关的非注释行
        lines = []
        for line in content.split("\n"):
            line_lower = line.lower()
            if "github" in line_lower and "#" not in line:
                continue
            lines.append(line.strip())
        
        # 添加新的github条目，确保格式统一
        lines.extend([f"{v}    {k}" for k, v in github_ips.items()])
        
        # 写入文件，使用原编码或UTF-8
        with open(HOSTS_PATH, "wb") as f:
            f.write("\n".join(lines).encode("utf-8"))
        
        # 刷新DNS缓存
        os.system("ipconfig /flushdns")
        return {"success": True, "message": "Hosts文件更新成功"}
    except Exception as e:
        return {"success": False, "error": str(e), "details": "可能需要管理员权限或文件被占用"}

def main():
    result = update_hosts()
    return result

if __name__ == "__main__":
    main()
