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
    
    # 导入故障分析模块，用于记录修复信息
    import trace.fault_analysis as fault_analysis

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

    # 导入连接诊断模块，用于TCP测试
    import trace.connection_diagnostic as connection_diagnostic
    
    # 获取所有可能的IP来源
    all_ips = []
    ip_sources = []
    
    print_step(2, "多源IP获取")
    
    # 1. DNS解析
    print("  [1/5] DNS解析获取IP")
    ips = get_dns_ips()
    if ips:
        print(f"    ✓ 获取到 {len(ips)} 个可用 IP")
        all_ips.extend(ips)
        ip_sources.extend(["dns"] * len(ips))
    else:
        print("    ✗ DNS解析失败")

    # 2. 备用DNS查找
    if not all_ips:
        print("  [2/5] 备用DNS查找")
        fallback_ips = fallback_dns_lookup()
        if fallback_ips:
            print(f"    ✓ 获取到 {len(fallback_ips)} 个备用 IP")
            all_ips.extend(fallback_ips)
            ip_sources.extend(["fallback_dns"] * len(fallback_ips))
        else:
            print("    ✗ 备用DNS查找失败")

    # 3. 已知良好IP
    print("  [3/5] 已知良好IP")
    known_ips = fallback_known_ips()
    if known_ips:
        print(f"    ✓ 获取到 {len(known_ips)} 个已知良好 IP")
        all_ips.extend(known_ips)
        ip_sources.extend(["known_good"] * len(known_ips))

    # 4. IP质量数据库
    print("  [4/5] IP质量数据库")
    db_ips = fallback_ip_quality_db()
    if db_ips:
        print(f"    ✓ 获取到 {len(db_ips)} 个高质量 IP")
        all_ips.extend(db_ips)
        ip_sources.extend(["quality_db"] * len(db_ips))

    # 5. 快速测试筛选
    print("  [5/5] 快速测试筛选")
    quick_test_ips = fallback_quick_test(get_known_good_ips())
    if quick_test_ips:
        print(f"    ✓ 获取到 {len(quick_test_ips)} 个快速测试通过 IP")
        all_ips.extend(quick_test_ips)
        ip_sources.extend(["quick_test"] * len(quick_test_ips))

    # 去重并保持顺序
    unique_ips = []
    unique_sources = []
    seen_ips = set()
    for ip, source in zip(all_ips, ip_sources):
        if ip not in seen_ips:
            seen_ips.add(ip)
            unique_ips.append(ip)
            unique_sources.append(source)
    
    all_ips = unique_ips
    ip_sources = unique_sources
    
    if not all_ips:
        print("  ✗ 无法获取任何IP")
        # 记录修复失败
        fault_analysis.log_repair(
            scheme="hosts_update",
            success=False,
            fault_type="dns_failure",
            details={
                "reason": f"连接状态：{current_status}，延迟：{current_ms}ms",
                "fix_method": "无法获取可用IP",
                "verification": "失败"
            }
        )
        return {**fallback_manual_config(), "success": False, "action": "fail", "message": "无法获取IP"}
    
    print(f"  总共获取到 {len(all_ips)} 个唯一 IP")

    print_step(3, "智能IP测试与筛选")
    
    # 优化IP测试策略：先测试TCP连接，再测速
    print("  先测试TCP连接，筛选可用IP...")
    tcp_test_results = []
    for ip in all_ips[:20]:  # 最多测试20个IP
        tcp_result = connection_diagnostic.test_multiple_ports(ip)
        if any(tcp_result.values()):
            tcp_test_results.append((ip, tcp_result))
    
    available_ips = [ip for ip, _ in tcp_test_results]
    
    if not available_ips:
        print("  ✗ 所有IP TCP连接测试失败，尝试使用已知良好IP直接修复")
        available_ips = get_known_good_ips()[:5]
    
    print(f"  经过TCP测试，{len(available_ips)} 个IP可用")
    
    # 对可用IP进行测速
    if len(available_ips) <= 10:
        results = test_ips(available_ips)
    else:
        print(f"  IP较多({len(available_ips)}个)，进行完整测速...")
        results = test_ips(available_ips)

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

    print_step(4, "多策略修复尝试")
    
    # 修复策略列表
    repair_strategies = [
        ("multi_ip", "多IP修复方案"),
        ("single_ip", "单IP修复方案"),
        ("minimal_ip", "最小化IP修复方案")
    ]
    
    repair_success = False
    final_ips = None
    used_strategy = None
    
    for strategy_name, strategy_desc in repair_strategies:
        print(f"  [{strategy_name}] {strategy_desc}")
        
        if strategy_name == "multi_ip" and len(valid_results) >= 2:
            # 多IP修复方案
            github_com_ip = valid_results[0]["ip"]
            api_github_ip = valid_results[1]["ip"]
            github_ips = {
                "github.com": github_com_ip,
                "api.github.com": api_github_ip
            }
            
            repair_result = try_hosts_repair_with_fallback(github_ips)
            if repair_result["success"]:
                final_ips = github_ips
                used_strategy = strategy_name
                break
            else:
                print(f"    ✗ {strategy_desc}失败: {repair_result.get('error', '未知错误')}")
        
        elif strategy_name == "single_ip":
            # 单IP修复方案
            single_ip = valid_results[0]["ip"]
            github_ips = {
                "github.com": single_ip,
                "api.github.com": single_ip
            }
            
            repair_result = update_hosts(github_ips=github_ips, backup=True)
            if repair_result["success"]:
                final_ips = github_ips
                used_strategy = strategy_name
                break
            else:
                print(f"    ✗ {strategy_desc}失败: {repair_result.get('error', '未知错误')}")
        
        elif strategy_name == "minimal_ip":
            # 最小化IP修复方案
            minimal_ip = valid_results[0]["ip"]
            github_ips = {
                "github.com": minimal_ip,
                "api.github.com": minimal_ip
            }
            
            repair_result = update_hosts(github_ips=github_ips, backup=True)
            if repair_result["success"]:
                final_ips = github_ips
                used_strategy = strategy_name
                break
            else:
                print(f"    ✗ {strategy_desc}失败: {repair_result.get('error', '未知错误')}")
    
    if not final_ips:
        print("  所有修复方案都失败")
        # 记录修复失败
        fault_analysis.log_repair(
            scheme="hosts_update",
            success=False,
            fault_type="hosts_failure",
            details={
                "reason": f"连接状态：{current_status}，延迟：{current_ms}ms",
                "fix_method": "所有修复策略均失败",
                "verification": "失败"
            }
        )
        return {**fallback_manual_config(), "success": False, "action": "fail", "message": "hosts修复失败"}
    
    print(f"  ✓ 使用{repair_strategies[[s[0] for s in repair_strategies].index(used_strategy)][1]}成功")
    print(f"  已更新 hosts: {', '.join([f'{k} → {v}' for k, v in final_ips.items()])}")

    print_step(5, "全面验证修复结果")
    print("  等待 DNS 刷新...")
    
    # 全面刷新网络设置
    print("  刷新网络缓存...")
    network_commands = [
        "ipconfig /flushdns",
        "ipconfig /registerdns",
        "netsh winsock reset",
        "netsh int ip reset"
    ]
    
    for cmd in network_commands:
        print(f"    执行: {cmd}")
        os.system(cmd)
        time.sleep(1)
    
    # 增加等待时间，确保网络设置完全刷新
    time.sleep(8)
    
    # 多次重试检查，提高验证准确性
    max_retries = 6
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
            print(f"    当前状态: {final_check['status'].upper()}, 等待重试...")
            time.sleep(5)
    
    if success:
        print(f"  ✓ 修复成功！当前状态: {final_result['status'].upper()} ({final_result['ms']}ms)")
        # 记录修复成功
        fault_analysis.log_repair(
            scheme="hosts_update",
            success=True,
            fault_type="connection_failure",
            details={
                "reason": f"连接状态：{current_status}，延迟：{current_ms}ms",
                "fix_method": f"{repair_strategies[[s[0] for s in repair_strategies].index(used_strategy)][1]}: {', '.join([f'{k} → {v}' for k, v in final_ips.items()])}",
                "verification": f"成功，当前状态: {final_result['status']}, 延迟: {final_result['ms']}ms",
                "strategy": used_strategy
            }
        )
        return {"success": True, "action": "fixed", "message": "修复成功", "ips": final_ips, "strategy": used_strategy}
    else:
        print("  ✗ 修复后仍无法连接..")
    
    print_step(6, "深度诊断与最终尝试")
    print("  尝试最后的深度诊断方案...")
    
    # 深度诊断：使用已知良好IP列表
    final_ips_list = get_known_good_ips()[:5]
    network_commands = [
        "ipconfig /flushdns",
        "ipconfig /registerdns",
        "netsh winsock reset",
        "netsh int ip reset"
    ]
    
    for ip in final_ips_list:
        print(f"    尝试已知良好IP: {ip}...")
        temp_ips = {
            "github.com": ip,
            "api.github.com": ip
        }
        
        if update_hosts(github_ips=temp_ips, backup=False)["success"]:
            # 刷新网络设置
            print("      刷新网络设置...")
            for cmd in network_commands:
                os.system(cmd)
            time.sleep(5)
            
            # 多次检查该IP
            for sub_retry in range(4):
                final_check = check_github()
                if final_check["status"] != "bad":
                    print(f"      ✓ 使用 {ip} 修复成功! 当前状态: {final_check['status'].upper()} ({final_check['ms']}ms)")
                    # 记录修复成功
                    fault_analysis.log_repair(
                        scheme="hosts_update",
                        success=True,
                        fault_type="connection_failure",
                        details={
                            "reason": f"连接状态：{current_status}，延迟：{current_ms}ms",
                            "fix_method": f"深度诊断：使用已知良好IP {ip}",
                            "verification": f"成功，当前状态: {final_check['status']}, 延迟: {final_check['ms']}ms",
                            "strategy": "deep_diagnosis"
                        }
                    )
                    return {"success": True, "action": "fixed", "message": "修复成功", "ips": temp_ips, "strategy": "deep_diagnosis"}
                else:
                    print(f"      当前状态: {final_check['status'].upper()}, 等待重试...")
                    time.sleep(3)
    
    print("  ✗ 所有修复方案均失败")
    print("\n  建议手动尝试:")
    print("    1. 检查网络防火墙设置")
    print("    2. 尝试更换网络环境")
    print("    3. 使用代理服务器")
    print("    4. 联系网络管理员")
    
    # 记录修复失败
    fault_analysis.log_repair(
        scheme="hosts_update",
        success=False,
        fault_type="connection_failure",
        details={
            "reason": f"连接状态：{current_status}，延迟：{current_ms}ms",
            "fix_method": "所有修复方案均失败",
            "verification": "失败",
            "suggestions": [
                "检查网络防火墙设置",
                "尝试更换网络环境",
                "使用代理服务器",
                "联系网络管理员"
            ]
        }
    )
    return {**fallback_manual_config(), "success": False, "action": "fail", "message": "修复后仍异常"}


if __name__ == "__main__":
    run()
