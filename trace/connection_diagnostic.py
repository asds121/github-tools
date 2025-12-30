#!/usr/bin/env python3
"""连接诊断 - 详细诊断 GitHub 连接问题，定位故障环节"""
import socket
import subprocess
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
test_single = tester_module.test_homepage_speed


def ping_host(host, count=1, timeout=2000):
    """ping 主机"""
    try:
        result = subprocess.run(
            ["ping", "-n", str(count), "-w", str(timeout), host],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except Exception:
        return False


def check_local_network():
    """检查本地网络连通性"""
    print("\n[1/5] 本地网络检查")
    print("-" * 40)

    checks = {
        "网关": "192.168.1.1",
        "DNS": "114.114.114.114",
        "互联网": "8.8.8.8"
    }

    results = {}
    for name, host in checks.items():
        success = ping_host(host)
        symbol = "✓" if success else "✗"
        results[name] = success
        print(f"  {symbol} {name}可达: {host}")

    print("\n  提示: 如已配置 hosts 文件，可绕过 DNS 直接访问")
    return results


def check_dns_resolution():
    """检查 DNS 解析"""
    print("\n[2/5] DNS 解析检查")
    print("-" * 40)

    print("  正在解析 github.com...")
    ips = get_dns_ips()

    if ips:
        print(f"  ✓ DNS 解析成功")
        print(f"    解析结果: {', '.join(ips[:5])}{'...' if len(ips) > 5 else ''}")
        return True, ips
    else:
        print("  ✗ DNS 解析失败，无法获取 IP")
        return False, []


def check_tcp_connection(ips):
    """检查 TCP 连接"""
    print("\n[3/5] TCP 连接检查")
    print("-" * 40)

    if not ips:
        print("  ✗ 无可用 IP 进行连接检查")
        return {}

    results = {}
    for ip in ips[:5]:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            start = time.time()
            sock.connect((ip, 443))
            latency = int((time.time() - start) * 1000)
            sock.close()
            symbol = "✓"
            results[ip] = True
            print(f"  {symbol} {ip}:443 - 连接成功 ({latency}ms)")
        except Exception as e:
            symbol = "✗"
            results[ip] = False
            print(f"  {symbol} {ip}:443 - 连接失败 ({type(e).__name__})")

    return results


def check_http_response(ips):
    """检查 HTTP 响应"""
    print("\n[4/5] HTTP 响应检查")
    print("-" * 40)

    if not ips:
        print("  ✗ 无可用 IP 进行 HTTP 检查")
        return {}

    results = {}
    for ip in ips[:3]:
        result = test_single(ip)
        if result.get("latency"):
            symbol = "✓"
            results[ip] = True
            print(f"  {symbol} GET / HTTP/1.1 - 响应成功 ({result['latency']}ms)")
        else:
            symbol = "✗"
            results[ip] = False
            print(f"  {symbol} GET / HTTP/1.1 - 无响应")

    return results


def get_assessment(local_results, dns_ok, tcp_results, http_results):
    """综合评估"""
    print("\n[5/5] 综合评估")
    print("-" * 40)

    tcp_ok = any(tcp_results.values())
    http_ok = any(http_results.values())

    local_ok = local_results.get("网关", False)
    dns_reachable = local_results.get("DNS", False)
    internet_ok = local_results.get("互联网", False)

    if tcp_ok and http_ok:
        status = "正常"
        suggestion = "GitHub 可正常访问"
        level = "success"
    elif not tcp_ok and not http_ok:
        if local_ok and (dns_reachable or internet_ok):
            status = "GitHub 连接故障"
            suggestion = "可能是 TCP/HTTPS 被阻断，尝试使用代理或检查防火墙"
            level = "error"
        elif not local_ok and not dns_reachable:
            status = "本地网络故障"
            suggestion = "检查网关和网络配置，DNS 不可达但 hosts 可绕过"
            level = "error"
        else:
            status = "网络连接异常"
            suggestion = "请检查网络连接或尝试使用代理"
            level = "error"
    else:
        status = "连接不稳定"
        suggestion = "可能是临时网络波动"
        level = "warning"

    print(f"  连接状态: {status}")
    print(f"  建议: {suggestion}")

    return {
        "status": status,
        "suggestion": suggestion,
        "level": level,
        "local_results": local_results,
        "dns_ok": dns_ok,
        "tcp_ok": tcp_ok,
        "http_ok": http_ok
    }


def run():
    print("=" * 60)
    print("GitHub 连接诊断")
    print("=" * 60)

    local_results = check_local_network()
    dns_ok, ips = check_dns_resolution()
    tcp_results = check_tcp_connection(ips)
    http_results = check_http_response(ips)
    assessment = get_assessment(local_results, dns_ok, tcp_results, http_results)

    print("\n" + "=" * 60)
    print("诊断完成")
    print("=" * 60)

    return assessment


if __name__ == "__main__":
    run()
