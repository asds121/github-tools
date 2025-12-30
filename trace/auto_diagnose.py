#!/usr/bin/env python3
"""一键检测修复 - 自动检测并修复GitHub连接问题"""
import sys
import time
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from github_utils import load_module

ROOT_DIR = Path(__file__).resolve().parent.parent

IP_QUALITY_DB = ROOT_DIR / "trace" / "ip_quality_db.json"

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


def load_ip_quality_db():
    """加载IP质量数据库"""
    try:
        if IP_QUALITY_DB.exists():
            return json.loads(IP_QUALITY_DB.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def save_ip_quality(ip, latency, success):
    """保存IP质量数据"""
    try:
        db = load_ip_quality_db()
        if ip not in db:
            db[ip] = {"count": 0, "total_latency": 0, "success_count": 0}
        db[ip]["count"] += 1
        if latency:
            db[ip]["total_latency"] += latency
        if success:
            db[ip]["success_count"] += 1
        IP_QUALITY_DB.write_text(json.dumps(db, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


def get_known_good_ips():
    """获取已知的可用IP列表（配置中的备用IP）"""
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


def print_step(step_num, message):
    print(f"\n{'=' * 50}")
    print(f"[{step_num}/6] {message}")
    print('=' * 50)


def fallback_dns_lookup():
    """备用方案1: 尝试更多DNS服务器"""
    print("\n【备用方案1】尝试更多DNS服务器...")
    try:
        import socket
        dns_servers = ["8.8.8.8", "8.8.4.4", "1.1.1.1", "9.9.9.9", "208.67.222.222"]
        ips = []
        for server in dns_servers:
            try:
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
    db = load_ip_quality_db()
    if not db:
        print("  IP质量库为空")
        return []
    
    candidates = []
    for ip, data in db.items():
        if data.get("success_count", 0) > 0 and data.get("count", 0) >= 2:
            avg_latency = data["total_latency"] / data["count"]
            candidates.append((ip, avg_latency, data["success_count"] / data["count"]))
    
    candidates.sort(key=lambda x: (x[2], x[1]))
    if candidates:
        print(f"  从质量库选择了 {min(5, len(candidates))} 个高分IP")
        return [c[0] for c in candidates[:5]]
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
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((ip, port))
        s.close()
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


def try_hosts_repair_with_fallback(github_ips):
    """尝试修复hosts，失败时提供备用方案"""
    if not is_admin():
        return {"success": False, "error": "需要管理员权限", "fallback": "manual"}
    
    result = update_hosts(github_ips=github_ips, backup=True)
    if result["success"]:
        return result
    
    print(f"  hosts写入失败: {result.get('error', '未知错误')}")
    return result


def run():
    print("=" * 60)
    print("GitHub 一键检测修复")
    print("=" * 60)

    print_step(1, "检测连接状态")
    result = check_github()
    current_status = result["status"]
    current_ms = result.get("ms", 0)
    
    if current_status == "bad":
        print(f"  ✗ 连接失败（{current_ms:.0f}ms），开始自动修复...")
    elif current_status == "warn":
        print(f"  ⚠ 连接超时/高延迟（{current_ms:.0f}ms > 3000ms），尝试优化...")
    else:
        print(f"  ✓ GitHub 连接正常（{current_ms:.0f}ms），无需修复")
        return {"success": True, "action": "skip", "message": "连接正常", "latency": current_ms}

    print("  ✗ 连接异常，开始自动修复...")

    all_ips = []
    
    print_step(2, "解析 DNS")
    ips = get_dns_ips()
    if ips:
        print(f"  获取到 {len(ips)} 个可用 IP")
        all_ips.extend(ips)

    if not all_ips:
        print("  DNS解析失败，尝试备用方案...")
        all_ips = fallback_dns_lookup()

    if not all_ips:
        all_ips = fallback_known_ips()

    db_ips = fallback_ip_quality_db()
    if db_ips:
        all_ips.extend(db_ips)

    all_ips = list(dict.fromkeys(all_ips))
    if not all_ips:
        print("  无法获取任何IP")
        return {**fallback_manual_config(), "success": False, "action": "fail", "message": "无法获取IP"}

    print_step(3, "测速选择最优 IP")
    
    if len(all_ips) <= 15:
        results = test_ips(all_ips)
    else:
        print(f"  IP较多({len(all_ips)}个)，先快速筛选...")
        quick_results = []
        for ip in all_ips:
            if test_single_ip(ip):
                quick_results.append(ip)
            if len(quick_results) >= 15:
                break
        if quick_results:
            results = test_ips(quick_results)
        else:
            results = test_ips(all_ips[:15])

    results.sort(key=lambda x: x.get("latency", float("inf")) or float("inf"))
    print("\n  测速结果 (Top 5):")
    for i, r in enumerate(results[:5], 1):
        latency = f"{r.get('latency', 'N/A')}ms" if r.get("latency") else "FAIL"
        ip = r.get('ip', 'Unknown')
        print(f"    {i}. {ip}: {latency}")

    if not results or not results[0].get("latency"):
        print("  所有IP测速失败，尝试备用方案...")
        good_ips = fallback_quick_test(get_known_good_ips())
        if good_ips:
            results = [{"ip": ip, "latency": None} for ip in good_ips]
            results[0]["latency"] = 100
        else:
            return {**fallback_manual_config(), "success": False, "action": "fail", "message": "所有IP测速失败"}

    valid_results = [r for r in results if r.get("latency")]
    
    for r in results:
        save_ip_quality(r.get("ip"), r.get("latency"), r.get("latency") is not None)

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
        return {**fallback_manual_config(), "success": False, "action": "fail", "message": "没有可用的IP"}

    print_step(4, "修复 hosts")
    
    github_ips = {
        "github.com": github_com_ip,
        "api.github.com": api_github_ip
    }
    
    repair_result = try_hosts_repair_with_fallback(github_ips)
    
    if not repair_result["success"]:
        print(f"  修复失败: {repair_result.get('error', '未知错误')}")
        print("\n  尝试使用单个IP修复...")
        single_ip = github_com_ip
        single_result = update_hosts(github_ips={"github.com": single_ip}, backup=True)
        if single_result["success"]:
            print(f"  ✓ 单IP修复成功: {single_ip}")
            github_ips = {"github.com": single_ip}
            repair_result = single_result
        else:
            print("  所有修复方案都失败")
            return {**fallback_manual_config(), "success": False, "action": "fail", "message": "hosts修复失败"}
    
    print(f"  已更新 hosts: github.com → {github_com_ip}, api.github.com → {api_github_ip}")

    print_step(5, "验证修复结果")
    print("  等待 DNS 刷新...")
    time.sleep(2)

    final_check = check_github()
    if final_check["status"] != "bad":
        print("  ✓ 修复成功，GitHub 已恢复正常")
        return {"success": True, "action": "fixed", "message": "修复成功", "ips": github_ips}
    else:
        print("  ✗ 修复后仍无法连接")
        print_step(6, "深度诊断")
        print("  尝试最后的方法...")
        for ip in get_known_good_ips()[:3]:
            print(f"    尝试 {ip}...")
            temp_ips = {"github.com": ip}
            if update_hosts(github_ips=temp_ips, backup=False)["success"]:
                time.sleep(2)
                if check_github()["status"] != "bad":
                    print(f"  ✓ 使用 {ip} 成功!")
                    return {"success": True, "action": "fixed", "message": f"最终方案成功: {ip}", "ips": temp_ips}
        
        print("  自动修复完全失败")
        return {**fallback_manual_config(), "success": False, "action": "fail", "message": "修复后仍异常"}


if __name__ == "__main__":
    run()
