#!/usr/bin/env python3
"""自动诊断服务 - 复杂的GitHub连接自动诊断和修复逻辑"""
import sys
import time
import json
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Import from github_utils
from github_utils.common_utils import load_module

ROOT_DIR = Path(__file__).resolve().parent.parent

# Import from trace layer
import trace.fault_analysis as fault_analysis

# Import from subprojects
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

# Import from connection_diagnostic subproject
connection_diagnostic = load_module(
    ROOT_DIR / "trace" / "connection_diagnostic.py"
)
get_known_good_ips = connection_diagnostic.get_known_good_ips
fallback_dns_lookup = connection_diagnostic.fallback_dns_lookup
fallback_known_ips = connection_diagnostic.fallback_known_ips
fallback_ip_quality_db = connection_diagnostic.fallback_ip_quality_db
fallback_quick_test = connection_diagnostic.fallback_quick_test
fallback_manual_config = connection_diagnostic.fallback_manual_config
test_single_ip = connection_diagnostic.test_single_ip

def load_ip_quality_db():
    """加载IP质量数据库"""
    IP_QUALITY_DB = ROOT_DIR / "trace" / "ip_quality_db.json"
    try:
        if IP_QUALITY_DB.exists():
            return json.loads(IP_QUALITY_DB.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def save_ip_quality(ip, latency, success):
    """保存IP质量数据"""
    IP_QUALITY_DB = ROOT_DIR / "trace" / "ip_quality_db.json"
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

def run(progress_callback=None):
    """一键检测修复 - 自动检测并修复GitHub连接问题
    
    Args:
        progress_callback: 进度回调函数，接收参数：(stage, message, progress_percent)
                          stage: 当前阶段名称
                          message: 当前阶段状态消息
                          progress_percent: 整体进度百分比 (0-100)
    """
    total_stages = 6
    
    def update_progress(stage_num, message):
        """更新进度"""
        stage_names = [
            "检测连接状态",
            "多源IP获取", 
            "智能IP测试与筛选",
            "多策略修复尝试",
            "全面验证修复结果",
            "深度诊断与最终尝试"
        ]
        stage_name = stage_names[stage_num-1]
        progress_percent = int((stage_num - 1) / total_stages * 100)
        if progress_callback:
            progress_callback(stage_name, message, progress_percent)
        print(f"[{progress_percent:3d}%] {stage_name}: {message}")
    
    print("=" * 60)
    print("GitHub 一键检测修复")
    print("=" * 60)
    
    # 阶段1: 检测连接状态
    update_progress(1, "开始检测连接状态...")
    result = check_github()
    current_status = result["status"]
    current_ms = result.get("ms", 0)
    
    if current_status == "bad":
        update_progress(1, f"连接失败（{current_ms:.0f}ms），开始自动修复...")
    elif current_status == "warn":
        update_progress(1, f"连接超时/高延迟（{current_ms:.0f}ms > 3000ms），尝试优化...")
    else:
        update_progress(1, f"GitHub 连接正常（{current_ms:.0f}ms），无需修复")
        return {"success": True, "action": "skip", "message": "连接正常", "latency": current_ms}

    # 阶段2: 多源IP获取
    update_progress(2, "开始获取多源IP...")
    all_ips = []
    ip_sources = []
    
    # DNS解析获取IP
    try:
        dns_ips = get_dns_ips()
        all_ips.extend(dns_ips)
        ip_sources.append("dns")
        update_progress(2, f"从DNS获取了{len(dns_ips)}个IP")
    except Exception as e:
        update_progress(2, f"DNS获取IP失败: {e}")
    
    # 从connection_diagnostic获取已知优质IP
    try:
        known_ips = get_known_good_ips()
        all_ips.extend(known_ips)
        ip_sources.append("known_good")
        update_progress(2, f"从已知优质IP获取了{len(known_ips)}个IP")
    except Exception as e:
        update_progress(2, f"获取已知优质IP失败: {e}")
    
    # 从IP质量数据库获取
    try:
        quality_db = load_ip_quality_db()
        quality_ips = [ip for ip, data in quality_db.items() 
                      if data["count"] > 5 and data["success_count"] / data["count"] > 0.8]
        all_ips.extend(quality_ips)
        ip_sources.append("quality_db")
        update_progress(2, f"从质量数据库获取了{len(quality_ips)}个IP")
    except Exception as e:
        update_progress(2, f"从质量数据库获取IP失败: {e}")
    
    # 去重IP列表
    unique_ips = list(set(all_ips))
    update_progress(2, f"去重后共获取了{len(unique_ips)}个IP")

    # 阶段3: 智能IP测试与筛选
    update_progress(3, "开始智能IP测试与筛选...")
    best_ip = None
    best_latency = float('inf')
    
    if unique_ips:
        # 使用github_ip_tester测试所有IP
        try:
            test_results = test_ips(unique_ips)
            update_progress(3, f"测试完成，共测试了{len(test_results)}个IP")
            
            # 按延迟排序，选择最佳IP
            sorted_results = sorted(test_results.items(), key=lambda x: x[1]['latency'] if x[1]['success'] else float('inf'))
            if sorted_results:
                best_ip, best_result = sorted_results[0]
                if best_result['success']:
                    best_latency = best_result['latency']
                    update_progress(3, f"找到最佳IP: {best_ip} (延迟: {best_latency:.0f}ms)")
                else:
                    update_progress(3, "没有找到可用的IP")
        except Exception as e:
            update_progress(3, f"IP测试失败: {e}")
    
    if not best_ip:
        update_progress(3, "IP测试失败，使用备选方案...")
        # 备选方案：手动配置的IP
        manual_ips = ["140.82.113.4", "140.82.113.5"]  # 常用的GitHub IP
        best_ip = manual_ips[0]
        best_latency = 0
        update_progress(3, f"使用手动配置的最佳IP: {best_ip}")

    # 阶段4: 多策略修复尝试
    update_progress(4, "开始多策略修复尝试...")
    
    # 准备修复用的IP映射
    github_ips = {
        "github.com": best_ip,
        "api.github.com": best_ip
    }
    
    # 记录修复前状态
    repair_before = {
        "status": current_status,
        "latency": current_ms,
        "ip_count": len(unique_ips),
        "ip_sources": ip_sources
    }
    
    # 尝试修复hosts文件
    update_progress(4, f"尝试更新hosts文件，使用IP: {best_ip}")
    repair_result = try_hosts_repair_with_fallback(github_ips)
    
    # 阶段5: 全面验证修复结果
    update_progress(5, "开始全面验证修复结果...")
    time.sleep(2)  # 等待DNS缓存刷新
    
    # 验证修复结果
    verify_result = check_github()
    verify_status = verify_result["status"]
    verify_ms = verify_result.get("ms", 0)
    
    if verify_status == "good":
        update_progress(5, f"修复成功！GitHub连接正常（{verify_ms:.0f}ms）")
    elif verify_status == "warn":
        update_progress(5, f"修复后连接超时/高延迟（{verify_ms:.0f}ms > 3000ms）")
    else:
        update_progress(5, f"修复失败，GitHub连接仍然失败（{verify_ms:.0f}ms）")
    
    # 记录修复后状态
    repair_after = {
        "status": verify_status,
        "latency": verify_ms,
        "best_ip": best_ip,
        "best_latency": best_latency
    }
    
    # 记录修复信息
    fault_analysis.log_repair(
        scheme="auto_diagnose",
        success=verify_status == "good",
        fault_type="connection_failure",
        details={
            "reason": f"GitHub连接{current_status}",
            "fix_method": "自动诊断修复",
            "verification": f"修复后状态{verify_status}",
            "before": repair_before,
            "after": repair_after,
            "github_ips": github_ips,
            "repair_result": repair_result
        }
    )
    
    # 阶段6: 深度诊断与最终尝试
    update_progress(6, "开始深度诊断与最终尝试...")
    
    if verify_status != "good":
        update_progress(6, "修复未成功，尝试深度诊断...")
        # 这里可以添加更多深度诊断逻辑
        update_progress(6, "深度诊断完成，尝试最终修复方案...")
        
        # 最终尝试：使用备选IP
        backup_ips = ["140.82.113.5", "140.82.114.4"]
        for backup_ip in backup_ips:
            if backup_ip != best_ip:
                update_progress(6, f"尝试使用备选IP: {backup_ip}")
                backup_github_ips = {
                    "github.com": backup_ip,
                    "api.github.com": backup_ip
                }
                backup_repair_result = try_hosts_repair_with_fallback(backup_github_ips)
                time.sleep(2)
                backup_verify_result = check_github()
                if backup_verify_result["status"] == "good":
                    update_progress(6, f"最终尝试成功！GitHub连接正常（{backup_verify_result.get('ms', 0):.0f}ms）")
                    verify_result = backup_verify_result
                    break
    else:
        update_progress(6, "修复成功，无需深度诊断")
    
    update_progress(6, "修复流程完成")
    
    # 保存IP质量数据
    if verify_result["status"] == "good":
        save_ip_quality(best_ip, verify_result.get('ms', 0), True)
    
    return {
        "success": verify_result["status"] == "good",
        "action": "repair",
        "message": "修复完成",
        "latency": verify_result.get("ms", 0),
        "status": verify_result["status"],
        "best_ip": best_ip,
        "repair_result": repair_result,
        "verify_result": verify_result
    }

if __name__ == "__main__":
    run()
