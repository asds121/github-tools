#!/usr/bin/env python3
"""一键测速 - 快速测试当前网络到 GitHub 的连接速度"""
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from github_utils import load_module, load_sub_config

ROOT_DIR = Path(__file__).resolve().parent.parent

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

config_ips = load_sub_config("GitHub-searcher-test-测速").get("ips", [])


def get_quality_level(avg_latency):
    if avg_latency < 100:
        return "优秀", "🟢"
    elif avg_latency < 200:
        return "良好", "🟡"
    elif avg_latency < 300:
        return "一般", "🟠"
    else:
        return "较差", "🔴"


def run():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("=" * 60)
    print("GitHub 一键测速")
    print("=" * 60)
    print(f"\n测试时间: {now}")
    print("-" * 50)

    ips = get_dns_ips()
    
    if not ips:
        print("  ✗ 无法解析 DNS，尝试使用配置中的 IP...")
        ips = config_ips
    elif len(ips) < 3 and config_ips:
        print(f"  ! DNS 仅返回 {len(ips)} 个 IP，补充配置中的 IP 一起测试")
        ips = list(set(ips + config_ips[:5]))
    
    if not ips:
        print("  ✗ 没有可用的 IP 进行测试")
        return {"success": False, "message": "没有可用 IP"}

    print(f"DNS 解析得到 {len(ips)} 个 IP")
    print("正在测速...\n")

    results = test_ips(ips)
    results.sort(key=lambda x: x.get("latency", float("inf")) or float("inf"))

    success_count = 0
    total_latency = 0
    valid_results = []

    for r in results:
        if r.get("latency"):
            latency = r["latency"]
            success_count += 1
            total_latency += latency
            valid_results.append(r)
            status = "✓"
        else:
            latency = "N/A"
            status = "✗"
        print(f"  {status} {r['ip']}: {latency}ms")

    if not valid_results:
        print("\n  ✗ 所有 IP 均无法连接")
        return {"success": False, "message": "所有 IP 测速失败"}

    fastest = valid_results[0]
    avg_latency = total_latency // success_count
    success_rate = (success_count / len(results)) * 100

    quality, emoji = get_quality_level(avg_latency)

    print("-" * 50)
    print(f"\n  最优 IP: {fastest['ip']} ({fastest['latency']}ms)")
    print(f"  平均延迟: {avg_latency}ms")
    print(f"  成功率: {success_count}/{len(results)} ({success_rate:.0f}%)")
    print(f"  连接质量: {emoji} {quality}")
    print()

    return {
        "success": True,
        "fastest_ip": fastest["ip"],
        "fastest_latency": fastest["latency"],
        "avg_latency": avg_latency,
        "success_rate": success_rate,
        "quality": quality,
        "results": valid_results
    }


if __name__ == "__main__":
    run()
