#!/usr/bin/env python3
"""连接诊断 - 详细诊断 GitHub 连接问题，定位故障环节"""
import socket
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import importlib.util
from pathlib import Path

# 导入故障分析模块，用于记录故障信息
from trace import fault_analysis

def load_module(module_path):
    """动态加载模块"""
    path = Path(module_path)
    spec = importlib.util.spec_from_file_location("tool_module", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

ROOT_DIR = Path(__file__).resolve().parent.parent


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

    # 常见网关地址列表，提高检测准确性
    common_gateways = ["192.168.1.1", "192.168.0.1", "10.0.0.1", "192.168.2.1", "192.168.10.1"]
    gateway = None
    for g in common_gateways:
        if ping_host(g):
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
        success = ping_host(host)
        symbol = "✓" if success else "✗"
        results[name] = success
        print(f"  {symbol} {name}可达: {host}")

    print("\n  提示: 如已配置 hosts 文件，可绕过 DNS 直接访问")
    return results


def get_known_good_ips():
    """获取已知的可用IP列表"""
    return [
        "140.82.113.3",
        "140.82.114.3",
        "140.82.112.3",
        "140.82.114.4",
        "140.82.113.4",
        "20.205.243.166",
        "20.205.243.165",
        "20.199.111.5",
        "20.27.177.113",
    ]


def fallback_dns_lookup():
    """备用方案1: 尝试更多DNS服务器"""
    print("\n【备用方案1】尝试更多DNS服务器...")
    try:
        dns_servers = ["8.8.8.8", "8.8.4.4", "1.1.1.1", "9.9.9.9", "208.67.222.222"]
        ips = []
        for server in dns_servers:
            try:
                import socket
                result = socket.gethostbyname_ex("github.com")
                for ip in result[2]:
                    if ip not in ips:
                        ips.append(ip)
            except Exception:
                continue
        if ips:
            print(f"  通过DNS解析获取到 {len(ips)} 个IP")
            return ips
    except Exception as e:
        print(f"  DNS解析失败: {e}")
    return []


def fallback_known_ips():
    """备用方案2: 使用已知的可用IP"""
    print("\n【备用方案2】使用已知可用IP...")
    known_ips = get_known_good_ips()
    print(f"  尝试 {len(known_ips)} 个已知可用IP...")
    return known_ips


def fallback_ip_quality_db():
    """备用方案3: 使用IP质量数据库中的成功IP"""
    print("\n【备用方案3】从IP质量库选择...")
    ip_quality_db_path = Path(__file__).resolve().parent / "ip_quality_db.json"
    try:
        if ip_quality_db_path.exists():
            import json
            db = json.loads(ip_quality_db_path.read_text(encoding="utf-8"))
            if db:
                candidates = []
                for ip, data in db.items():
                    if data.get("success_count", 0) > 0 and data.get("count", 0) >= 2:
                        avg_latency = data["total_latency"] / data["count"]
                        candidates.append((ip, avg_latency, data["success_count"] / data["count"]))
                
                candidates.sort(key=lambda x: (x[2], x[1]))
                if candidates:
                    print(f"  从质量库选择了 {min(5, len(candidates))} 个高分IP")
                    return [c[0] for c in candidates[:5]]
    except Exception:
        pass
    print("  IP质量库为空或读取失败")
    return []


def fallback_quick_test(ips):
    """备用方案4: 快速测试IP"""
    print("\n【备用方案4】快速测试...")
    results = []
    for ip in ips[:10]:
        if test_single_ip(ip):
            results.append(ip)
    if results:
        print(f"  快速测试找到 {len(results)} 个可用IP")
        return results
    return []


def test_single_ip(ip, port=443, timeout=2):
    """快速测试单个IP"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((ip, port))
        sock.close()
        return True
    except Exception:
        return False


def fallback_manual_config():
    """备用方案5: 提供手动配置建议"""
    print("\n【备用方案5】手动配置建议")
    print("  1. 检查网络连接是否正常")
    print("  2. 尝试使用VPN或代理")
    print("  3. 手动编辑 hosts 文件，添加:")
    known_ips = get_known_good_ips()
    for ip in known_ips[:3]:
        print(f"     {ip}    github.com")
    print("  4. 运行: ipconfig /flushdns 刷新DNS")
    return {"manual": True}


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
    
    # 如果所有HTTP响应都失败，记录HTTP故障
    if all_failed:
        fault_analysis.log_fault(
            "http_failure",
            details={"ips": ips[:3], "reason": "所有IP的HTTP响应都失败"}
        )

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

    print("\n[0/6] 快速连通性检查")
    print("-" * 40)

    quick_check = check_github()
    if quick_check["status"] != "bad":
        avg_ms = quick_check.get("ms", 0)
        print(f"  ✓ GitHub 连接正常 ({avg_ms:.0f}ms)")
        print("\n" + "=" * 60)
        print("诊断完成 - 无需深入诊断")
        print("=" * 60)
        return {
            "status": "正常",
            "suggestion": "GitHub 可正常访问",
            "level": "success",
            "latency": avg_ms
        }

    print("  ✗ 连通性异常，开始详细诊断...")

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
