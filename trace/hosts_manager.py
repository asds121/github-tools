#!/usr/bin/env python3
"""Hosts 管理器 - 查看、编辑、备份 GitHub hosts 配置"""
import os
import ctypes
from datetime import datetime
from pathlib import Path

HOSTS_PATH = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32", "drivers", "etc", "hosts")
BACKUP_DIR = Path(__file__).parent / "backups"

GITHUB_DOMAINS = ["github.com", "api.github.com", "gist.github.com", "assets-cdn.github.com"]


def is_admin():
    """检查是否具有管理员权限"""
    try:
        return os.getuid() == 0
    except AttributeError:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0


def get_hosts_content():
    """读取 hosts 文件内容"""
    try:
        with open(HOSTS_PATH, "rb") as f:
            return f.read().decode("gbk", errors="ignore")
    except Exception:
        return None


def get_github_entries(content):
    """提取 GitHub 相关的配置行"""
    entries = []
    for line in content.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        for domain in GITHUB_DOMAINS:
            if domain in line.lower():
                entries.append(line)
                break
    return entries


def list_backups():
    """列出所有备份文件"""
    BACKUP_DIR.mkdir(exist_ok=True)
    backups = list(BACKUP_DIR.glob("hosts_*.bak"))
    backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return backups


def create_backup():
    """创建 hosts 备份"""
    BACKUP_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"hosts_{timestamp}.bak"
    content = get_hosts_content()
    if content:
        backup_path.write_text(content, encoding="utf-8")
        return str(backup_path)
    return None


def restore_backup(backup_path):
    """从备份恢复 hosts 文件"""
    if not os.path.exists(backup_path):
        return False
    content = Path(backup_path).read_text(encoding="utf-8")
    try:
        with open(HOSTS_PATH, "wb") as f:
            f.write(content.encode("gbk"))
        return True
    except Exception:
        return False


def add_github_entry(ip, domain="github.com"):
    """添加 GitHub 配置"""
    if not is_admin():
        return False, "需要管理员权限"
    content = get_hosts_content()
    if content is None:
        return False, "无法读取 hosts 文件"
    line = f"{ip}    {domain}"
    new_content = content.rstrip() + "\n" + line + "\n"
    try:
        with open(HOSTS_PATH, "wb") as f:
            f.write(new_content.encode("gbk"))
        return True, "添加成功"
    except Exception as e:
        return False, str(e)


def remove_github_entries(lines_to_remove):
    """删除指定的 GitHub 配置行"""
    if not is_admin():
        return False, "需要管理员权限"
    content = get_hosts_content()
    if content is None:
        return False, "无法读取 hosts 文件"

    lines = content.split("\n")
    removed_count = 0
    new_lines = []
    remove_set = set(lines_to_remove)

    for line in lines:
        stripped = line.strip()
        if stripped in remove_set:
            removed_count += 1
        else:
            new_lines.append(line)

    try:
        with open(HOSTS_PATH, "wb") as f:
            f.write("\n".join(new_lines).encode("gbk"))
        return True, f"已删除 {removed_count} 行"
    except Exception as e:
        return False, str(e)


def get_status():
    """获取当前 hosts 状态"""
    content = get_hosts_content()
    if content is None:
        return {
            "readable": False,
            "github_entries": [],
            "entry_count": 0,
            "backup_count": 0,
            "is_admin": is_admin()
        }

    entries = get_github_entries(content)
    backups = list_backups()

    return {
        "readable": True,
        "github_entries": entries,
        "entry_count": len(entries),
        "backup_count": len(backups),
        "is_admin": is_admin()
    }


def run():
    print("=" * 60)
    print("GitHub Hosts 管理器")
    print("=" * 60)

    status = get_status()
    if not status["readable"]:
        print("\n✗ 无法读取 hosts 文件")
        return

    print(f"\n【当前 GitHub 配置】(共 {status['entry_count']} 条)")
    print("-" * 50)

    if status["github_entries"]:
        for i, entry in enumerate(status["github_entries"], 1):
            print(f"  {i}. {entry}")
    else:
        print("  无 GitHub 相关配置")

    print(f"\n【备份管理】(共 {status['backup_count']} 个备份)")
    print("-" * 50)
    backups = list_backups()
    for i, backup in enumerate(backups[:5], 1):
        mtime = datetime.fromtimestamp(backup.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        print(f"  {i}. {backup.name} ({mtime})")
    if len(backups) > 5:
        print(f"  ... 共 {len(backups)} 个备份")

    print(f"\n【操作选项】")
    print("-" * 50)
    print("  [1] 备份当前配置")
    print("  [2] 恢复最近备份")
    print("  [3] 添加新配置")
    print("  [4] 删除配置")
    print("  [5] 刷新列表")

    print(f"\n  管理员权限: {'✓' if status['is_admin'] else '✗ (编辑需要管理员)'}")
    print()

    return status


if __name__ == "__main__":
    run()
