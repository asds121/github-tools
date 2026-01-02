#!/usr/bin/env python3
"""连接诊断服务 - 复杂的GitHub连接诊断逻辑"""
import socket
import subprocess
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Import from trace layer
from trace import fault_analysis
from trace import connection_diagnostic

# Import from subprojects
from github_utils.common_utils import load_module

ROOT_DIR = Path(__file__).resolve().parent.parent

# Load subproject modules
checker_module = load_module(
    ROOT_DIR / "github-checker-检测状态" / "github_checker.py"
)
check_github = checker_module.check

dns_module = load_module(
    ROOT_DIR / "GitHub-searcher-dns-DNS" / "github_dns.py"
)
get_dns_ips = dns_module.resolve_all

tester_module = load_module(
    ROOT_DIR / "GitHub-searcher-test-测速" / "github_ip_tester.py"
)
test_single = tester_module.test_homepage_speed


def check_local_network():
    """检查本地网络连通性"""
    print("\n[1/5] 本地网络检查")
    print("-" * 40)

    # 常见网关地址列表，提高检测准确性
    common_gateways = ["192.168.1.1", "192.168.0.1", "10.0.0.1", "192.168.2.1", "192.168.10.1"]
    gateway = None
    for g in common_gateways:
        if connection_diagnostic.ping_host(g):
            gateway = g
            break
    gateway = gateway or common_gateways[0]  # 默认使用192.168.1.1

    checks = {
        "网关": gateway,
        "DNS": "114.114.114.114",
        "互联网": "8.8.8.8"
    }

    results = {}
    for name, host in checks.items():
        success = connection_diagnostic.ping_host(host)
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
        print("  ✓ DNS 解析成功")
        print(f"    解析结果: {', '.join(ips[:5])}{'...' if len(ips) > 5 else ''}")
        return True, ips
    else:
        print("  ✗ DNS 解析失败，无法获取 IP")
        # 记录 DNS 故障
        fault_analysis.log_fault(
            "dns_failure",
            details={"reason": "无法解析 github.com", "domain": "github.com"}
        )
        return False, []


def check_tcp_connection(ips):
    """检查 TCP 连接"""
    print("\n[3/5] TCP 连接检查")
    print("-" * 40)

    if not ips:
        print("  ✗ 无可用 IP 进行连接检查")
        return {}

    results = {}
    all_failed = True
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
            all_failed = False
            print(f"  {symbol} {ip}:443 - 连接成功 ({latency}ms)")
        except socket.timeout:
            symbol = "✗"
            results[ip] = False
            print(f"  {symbol} {ip}:443 - 连接失败 (连接超时)")
        except ConnectionRefusedError:
            symbol = "✗"
            results[ip] = False
            print(f"  {symbol} {ip}:443 - 连接失败 (连接被拒绝)")
        except Exception as e:
            symbol = "✗"
            results[ip] = False
            print(f"  {symbol} {ip}:443 - 连接失败 ({type(e).__name__})")
    
    # 如果所有TCP连接都失败，记录TCP故障
    if all_failed:
        fault_analysis.log_fault(
            "tcp_failure",
            details={"ips": ips[:5], "reason": "所有IP的TCP连接都失败", "port": 443}
        )

    return results


def check_http_response(ips):
    """检查 HTTP 响应"""
    print("\n[4/5] HTTP 响应检查")
    print("-" * 40)

    if not ips:
        print("  ✗ 无可用 IP 进行 HTTP 检查")
        return {}

    results = {}
    all_failed = True
    for ip in ips[:3]:
        result = test_single(ip)
        if result.get("latency"):
            symbol = "✓"
            results[ip] = True
            all_failed = False
            print(f"  {symbol} GET / HTTP/1.1 - 响应成功 ({result['latency']}ms)")
        else:
            symbol = "✗"
            results[ip] = False
            error = result.get("error", "未知错误")
            print(f"  {symbol} GET / HTTP/1.1 - 无响应 ({error})")
    
    # 如果所有HTTP请求都失败，记录HTTP故障
    if all_failed:
        fault_analysis.log_fault(
            "http_failure",
            details={"ips": ips[:3], "reason": "所有IP的HTTP请求都失败", "port": 443}
        )

    return results


def diagnose_connection(progress_callback=None):
    """诊断 GitHub 连接问题"""
    print("\n" + "=" * 60)
    print("GitHub 连接诊断")
    print("=" * 60)
    
    # 阶段1: 检查本地网络
    if progress_callback:
        progress_callback("本地网络检查", "开始检查本地网络连通性", 0)
    local_network_ok = all(check_local_network().values())
    
    # 阶段2: 检查 GitHub 状态
    if progress_callback:
        progress_callback("GitHub状态检查", "开始检查GitHub整体状态", 25)
    github_status = check_github()
    print(f"\n[5/5] GitHub 状态检查")
    print("-" * 40)
    print(f"  当前状态: {github_status['status'].upper()}")
    print(f"  响应时间: {github_status['ms']}ms")
    for name, result in github_status["results"]:
        status = "✓" if result["ok"] else "✗"
        print(f"  {status} {name}: {'OK' if result['ok'] else 'FAIL'} ({result['ms']}ms)")
    
    # 阶段3: 检查 DNS 解析
    if progress_callback:
        progress_callback("DNS解析检查", "开始检查DNS解析功能", 50)
    dns_ok, ips = check_dns_resolution()
    
    # 阶段4: 检查 TCP 连接
    if progress_callback:
        progress_callback("TCP连接检查", "开始检查TCP连接能力", 75)
    tcp_ok = check_tcp_connection(ips)
    
    # 阶段5: 检查 HTTP 响应
    if progress_callback:
        progress_callback("HTTP响应检查", "开始检查HTTP响应能力", 100)
    http_ok = check_http_response(ips)
    
    # 生成诊断报告
    diagnosis = {
        "local_network": local_network_ok,
        "github_status": github_status,
        "dns_resolution": dns_ok,
        "tcp_connection": any(tcp_ok.values()) if tcp_ok else False,
        "http_response": any(http_ok.values()) if http_ok else False,
        "ips": ips,
        "tcp_results": tcp_ok,
        "http_results": http_ok
    }
    
    print("\n" + "=" * 60)
    print("诊断报告")
    print("=" * 60)
    print(f"  本地网络: {'✓ 正常' if diagnosis['local_network'] else '✗ 异常'}")
    print(f"  DNS 解析: {'✓ 正常' if diagnosis['dns_resolution'] else '✗ 异常'}")
    print(f"  TCP 连接: {'✓ 正常' if diagnosis['tcp_connection'] else '✗ 异常'}")
    print(f"  HTTP 响应: {'✓ 正常' if diagnosis['http_response'] else '✗ 异常'}")
    print(f"  GitHub 状态: {diagnosis['github_status']['status'].upper()}")
    print("=" * 60)
    
    return diagnosis


def run_diagnosis(progress_callback=None):
    """运行完整的连接诊断"""
    try:
        return diagnose_connection(progress_callback)
    except Exception as e:
        print(f"\n[错误] 诊断过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "message": "连接诊断失败"
        }

if __name__ == "__main__":
    run_diagnosis()
