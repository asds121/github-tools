#!/usr/bin/env python3
"""GitHub Hosts查看器 - 查看当前hosts配置"""
import os
from pathlib import Path

HOSTS_PATH = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32", "drivers", "etc", "hosts")

def get_hosts_content():
    """获取hosts文件内容（忽略注释）"""
    try:
        with open(HOSTS_PATH, "rb") as f:
            content = f.read().decode("gbk", errors="ignore")

        lines = []
        for line in content.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            lines.append(line)

        return lines
    except Exception as e:
        return [f"错误: {str(e)}"]

def view_github_entries():
    """只查看GitHub相关的hosts条目"""
    try:
        with open(HOSTS_PATH, "rb") as f:
            content = f.read().decode("gbk", errors="ignore")

        lines = []
        for line in content.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "github" in line.lower():
                lines.append(line)

        return lines if lines else ["未找到GitHub相关的hosts条目"]
    except Exception as e:
        return [f"错误: {str(e)}"]

def main():
    """主函数 - 查看所有非注释条目"""
    return get_hosts_content()

if __name__ == "__main__":
    result = main()
    for line in result:
        print(line)
