#!/usr/bin/env python3
"""一键检测修复 - 自动检测并修复GitHub连接问题"""
import sys
import time
import json
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Import from github_utils instead of defining locally
from github_utils.common_utils import load_module

ROOT_DIR = Path(__file__).resolve().parent.parent

IP_QUALITY_DB = ROOT_DIR / "trace" / "ip_quality_db.json"

# 从trace层导入备用方案函数
# 使用绝对导入，避免直接运行时的相对导入错误
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# 导入connection_diagnostic模块
import trace.connection_diagnostic as connection_diagnostic

# 从connection_diagnostic导入所需函数
get_known_good_ips = connection_diagnostic.get_known_good_ips
fallback_dns_lookup = connection_diagnostic.fallback_dns_lookup
fallback_known_ips = connection_diagnostic.fallback_known_ips
fallback_ip_quality_db = connection_diagnostic.fallback_ip_quality_db
fallback_quick_test = connection_diagnostic.fallback_quick_test
fallback_manual_config = connection_diagnostic.fallback_manual_config
test_single_ip = connection_diagnostic.test_single_ip

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
test_ips = tester_module.test_all

repair_module = load_module(
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


def print_step(step_num, message):
    print(f"\n{'='*50}")
    print(f"[{step_num}/6] {message}")
    print('='*50)


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
        "api.github.com": api_github_ip,
        "assets-cdn.github.com": api_github_ip,
        "raw.githubusercontent.com": api_github_ip
    }
    
    repair_result = try_hosts_repair_with_fallback(github_ips)
    
    if not repair_result["success"]:
        print(f"  修复失败: {repair_result.get('error', '未知错误')}")
        print("\n  尝试使用单个IP修复...")
        single_ip = github_com_ip
        single_result = update_hosts(github_ips={"github.com": single_ip}, backup=True)
        if single_result["success"]:
            print(f"  ✓ 单IP修复成功: {single_ip}")
            github_ips = {
                "github.com": single_ip,
                "api.github.com": single_ip,
                "assets-cdn.github.com": single_ip,
                "raw.githubusercontent.com": single_ip
            }
            repair_result = single_result
        else:
            print("  所有修复方案都失败")
            return {**fallback_manual_config(), "success": False, "action": "fail", "message": "hosts修复失败"}
    
    print(f"  已更新 hosts: github.com → {github_com_ip}, api.github.com → {api_github_ip}")

    print_step(5, "验证修复结果")
    print("  等待 DNS 刷新...")
    
    # 全面刷新网络设置
    print("  刷新 DNS 缓存...")
    for _ in range(2):
        os.system("ipconfig /flushdns")
        os.system("ipconfig /registerdns")
        time.sleep(1)
    
    # 增加等待时间，确保DNS完全刷新
    time.sleep(5)
    
    # 多次重试检查，提高验证准确性
    max_retries = 5
    success = False
    final_result = None
    
    for retry in range(max_retries):
        print(f"  第 {retry+1}/{max_retries} 次验证...")
        final_check = check_github()
        if final_check["status"] != "bad":
            success = True
            final_result = final_check
            break
        else:
            print(f"  当前状态: {final_check['status'].upper()}, 等待重试...")
            time.sleep(3)
    
    if success:
        print(f"  ✓ 修复成功！当前状态: {final_result['status'].upper()} ({final_result['ms']}ms)")
        return {"success": True, "action": "fixed", "message": "修复成功", "ips": github_ips}
    else:
        print("  ✗ 修复后仍无法连接..")
    
    print_step(6, "深度诊断")
    print("  尝试最后的方法...")
    final_ips = get_known_good_ips()[:3]
    
    for ip in final_ips:
        print(f"    尝试 {ip}...")
        temp_ips = {
            "github.com": ip,
            "api.github.com": ip,
            "assets-cdn.github.com": ip,
            "raw.githubusercontent.com": ip
        }
        
        if update_hosts(github_ips=temp_ips, backup=False)["success"]:
            # 全面刷新网络
            for _ in range(2):
                os.system("ipconfig /flushdns")
                os.system("ipconfig /registerdns")
                time.sleep(1)
            
            time.sleep(3)
            
            # 多次检查该IP
            for sub_retry in range(3):
                final_check = check_github()
                if final_check["status"] != "bad":
                    print(f"  ✓ 使用 {ip} 修复成功! 当前状态: {final_check['status'].upper()} ({final_check['ms']}ms)")
                    return {"success": True, "action": "fixed", "message": f"最终方案成功: {ip}", "ips": temp_ips}
                time.sleep(2)
    
    print("  自动修复完全失败...")
    return {**fallback_manual_config(), "success": False, "action": "fail", "message": "修复后仍异常"}


if __name__ == "__main__":
    run()
