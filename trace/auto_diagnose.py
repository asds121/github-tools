#!/usr/bin/env python3
"""一键检测修复 - 自动检测并修复GitHub连接问题"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from github_utils import load_module

ROOT_DIR = Path(__file__).resolve().parent.parent


checker_module = load_module(
    "checker",
    ROOT_DIR / "github-checker-检测状态" / "github_checker.py"
)
check_github = checker_module.check

dns_module = load_module(
    "dns",
    ROOT_DIR / "GitHub-searcher-dns-DNS" / "github_dns.py"
)
get_dns_ips = dns_module.resolve_all

tester_module = load_module(
    "tester",
    ROOT_DIR / "GitHub-searcher-test-测速" / "github_ip_tester.py"
)
test_ips = tester_module.test_all

repair_module = load_module(
    "repair",
    ROOT_DIR / "GitHub-repair-fix-修复" / "github_repair_fix.py"
)
update_hosts = repair_module.update_hosts
is_admin = repair_module.is_admin


def print_step(step_num, message):
    print(f"\n{'=' * 50}")
    print(f"[{step_num}/5] {message}")
    print('=' * 50)


def run():
    print("=" * 60)
    print("GitHub 一键检测修复")
    print("=" * 60)

    print_step(1, "检测连接状态")
    result = check_github()
    if result["status"] != "bad":
        print("  ✓ GitHub 连接正常，无需修复")
        return {"success": True, "action": "skip", "message": "连接正常"}

    print("  ✗ 连接异常，开始自动修复...")

    print_step(2, "解析 DNS")
    ips = get_dns_ips()
    if not ips:
        return {"success": False, "action": "fail", "message": "无法获取 IP"}
    print(f"  获取到 {len(ips)} 个可用 IP")

    print_step(3, "测速选择最优 IP")
    results = test_ips(ips)
    results.sort(key=lambda x: x.get("latency", float("inf")) or float("inf"))
    print("\n  测速结果 (Top 5):")
    for i, r in enumerate(results[:5], 1):
        latency = f"{r.get('latency', 'N/A')}ms" if r.get("latency") else "FAIL"
        ip = r.get('ip', 'Unknown')
        print(f"    {i}. {ip}: {latency}")

    if not results or not results[0].get("latency"):
        return {"success": False, "action": "fail", "message": "所有 IP 测速失败"}

    valid_results = [r for r in results if r.get("latency")]
    if len(valid_results) >= 2:
        github_com_ip = valid_results[0]["ip"]
        api_github_ip = valid_results[1]["ip"]
        print(f"  github.com → {github_com_ip} ({valid_results[0]['latency']}ms)")
        print(f"  api.github.com → {api_github_ip} ({valid_results[1]['latency']}ms)")
    elif len(valid_results) == 1:
        github_com_ip = valid_results[0]["ip"]
        api_github_ip = valid_results[0]["ip"]
        print(f"  只有一个可用 IP，两个域名共用: {github_com_ip}")
    else:
        return {"success": False, "action": "fail", "message": "没有可用的 IP"}

    print_step(4, "修复 hosts")
    if not is_admin():
        return {"success": False, "action": "fail", "message": "需要管理员权限"}

    github_ips = {
        "github.com": github_com_ip,
        "api.github.com": api_github_ip
    }
    result = update_hosts(github_ips=github_ips, backup=True)
    if not result["success"]:
        return {"success": False, "action": "fail", "message": result.get("error", "hosts 写入失败")}
    print(f"  已更新 hosts: github.com → {github_com_ip}, api.github.com → {api_github_ip}")

    print_step(5, "验证修复结果")
    print("  等待 DNS 刷新...")
    time.sleep(2)

    final_check = check_github()
    if final_check["status"] != "bad":
        print("  ✓ 修复成功，GitHub 已恢复正常")
        return {"success": True, "action": "fixed", "message": "修复成功"}
    else:
        print("  ✗ 修复后仍无法连接")
        return {"success": False, "action": "fail", "message": "修复后仍异常"}


if __name__ == "__main__":
    run()
