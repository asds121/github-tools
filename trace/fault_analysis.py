#!/usr/bin/env python3
"""故障分析 - 网络故障原因及修复成功记录统计"""
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "trace" / "data"
DATA_DIR.mkdir(exist_ok=True)

# 故障记录文件路径
FAULT_HISTORY = DATA_DIR / "fault_history.json"
REPAIR_HISTORY = DATA_DIR / "repair_history.json"

# 故障类型定义
FAULT_TYPES = {
    "dns_failure": "DNS解析失败",
    "tcp_failure": "TCP连接失败",
    "http_failure": "HTTP响应失败",
    "ssl_failure": "SSL证书错误",
    "timeout": "连接超时",
    "other": "其他故障"
}

# 修复方案定义
REPAIR_SCHEMES = {
    "hosts_update": "更新Hosts文件",
    "dns_change": "更换DNS服务器",
    "ip_switch": "切换IP地址",
    "proxy_use": "使用代理",
    "restart_network": "重启网络",
    "other": "其他修复方案"
}


def load_fault_history():
    """加载故障历史记录"""
    if FAULT_HISTORY.exists():
        try:
            with open(FAULT_HISTORY, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_fault_history(history):
    """保存故障历史记录"""
    with open(FAULT_HISTORY, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def load_repair_history():
    """加载修复历史记录"""
    if REPAIR_HISTORY.exists():
        try:
            with open(REPAIR_HISTORY, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_repair_history(history):
    """保存修复历史记录"""
    with open(REPAIR_HISTORY, "w", encoding="utf-8-sig") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def log_fault(fault_type, details=None, latency=None):
    """记录故障信息"""
    fault_record = {
        "timestamp": datetime.now().isoformat(),
        "fault_type": fault_type,
        "fault_name": FAULT_TYPES.get(fault_type, "未知故障"),
        "details": details or {},
        "latency": latency
    }
    
    history = load_fault_history()
    history.append(fault_record)
    save_fault_history(history)
    return fault_record


def log_repair(scheme, success, fault_type=None, details=None):
    """记录修复信息"""
    repair_record = {
        "timestamp": datetime.now().isoformat(),
        "scheme": scheme,
        "scheme_name": REPAIR_SCHEMES.get(scheme, "未知修复方案"),
        "success": success,
        "fault_type": fault_type,
        "details": details or {},
        "reason": details.get("reason", "未明确"),
        "fix_method": details.get("fix_method", "未记录"),
        "verification": details.get("verification", "未验证")
    }
    
    history = load_repair_history()
    history.append(repair_record)
    save_repair_history(history)
    return repair_record


def analyze_fault_trends(days=30):
    """分析故障趋势"""
    fault_history = load_fault_history()
    repair_history = load_repair_history()
    
    # 计算日期范围
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # 按日期分组故障记录
    daily_faults = defaultdict(list)
    for record in fault_history:
        record_date = datetime.fromisoformat(record["timestamp"])
        if start_date <= record_date <= end_date:
            date_key = record_date.strftime("%Y-%m-%d")
            daily_faults[date_key].append(record)
    
    # 按日期分组修复记录
    daily_repairs = defaultdict(list)
    for record in repair_history:
        record_date = datetime.fromisoformat(record["timestamp"])
        if start_date <= record_date <= end_date:
            date_key = record_date.strftime("%Y-%m-%d")
            daily_repairs[date_key].append(record)
    
    # 生成趋势数据
    trend_data = []
    current_date = start_date
    while current_date <= end_date:
        date_key = current_date.strftime("%Y-%m-%d")
        
        # 统计当日故障
        day_faults = daily_faults.get(date_key, [])
        day_repairs = daily_repairs.get(date_key, [])
        
        # 故障类型统计
        fault_type_count = defaultdict(int)
        for fault in day_faults:
            fault_type_count[fault["fault_type"]] += 1
        
        # 修复成功率统计
        total_repairs = len(day_repairs)
        successful_repairs = sum(1 for r in day_repairs if r["success"])
        success_rate = (successful_repairs / total_repairs * 100) if total_repairs > 0 else 0
        
        trend_data.append({
            "date": date_key,
            "fault_count": len(day_faults),
            "repair_count": total_repairs,
            "successful_repairs": successful_repairs,
            "success_rate": round(success_rate, 1),
            "fault_types": dict(fault_type_count)
        })
        
        current_date += timedelta(days=1)
    
    return trend_data


def analyze_fault_distribution(days=30):
    """分析故障类型分布"""
    fault_history = load_fault_history()
    
    # 计算日期范围
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # 统计故障类型
    fault_stats = defaultdict(lambda: {
        "count": 0,
        "name": "未知故障",
        "first_occurrence": None,
        "last_occurrence": None,
        "avg_latency": []
    })
    
    for record in fault_history:
        record_date = datetime.fromisoformat(record["timestamp"])
        if start_date <= record_date <= end_date:
            fault_type = record["fault_type"]
            fault_stats[fault_type]["count"] += 1
            fault_stats[fault_type]["name"] = record["fault_name"]
            
            # 更新首次和末次出现时间
            if fault_stats[fault_type]["first_occurrence"] is None:
                fault_stats[fault_type]["first_occurrence"] = record["timestamp"]
            fault_stats[fault_type]["last_occurrence"] = record["timestamp"]
            
            # 收集延迟数据
            if record["latency"]:
                fault_stats[fault_type]["avg_latency"].append(record["latency"])
    
    # 计算平均延迟
    for stats in fault_stats.values():
        if stats["avg_latency"]:
            stats["avg_latency"] = round(sum(stats["avg_latency"]) / len(stats["avg_latency"]), 1)
        else:
            stats["avg_latency"] = 0
    
    return dict(fault_stats)


def analyze_repair_effectiveness(days=30):
    """分析修复方案效果"""
    repair_history = load_repair_history()
    
    # 计算日期范围
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # 统计修复方案效果
    repair_stats = defaultdict(lambda: {
        "count": 0,
        "successful": 0,
        "name": "未知修复方案",
        "success_rate": 0
    })
    
    # 按故障类型统计修复效果
    fault_repair_stats = defaultdict(lambda: defaultdict(lambda: {
        "count": 0,
        "successful": 0,
        "success_rate": 0
    }))
    
    for record in repair_history:
        record_date = datetime.fromisoformat(record["timestamp"])
        if start_date <= record_date <= end_date:
            scheme = record["scheme"]
            success = record["success"]
            fault_type = record["fault_type"]
            
            # 总体修复方案统计
            repair_stats[scheme]["count"] += 1
            if success:
                repair_stats[scheme]["successful"] += 1
            repair_stats[scheme]["name"] = record["scheme_name"]
            
            # 按故障类型统计
            if fault_type:
                fault_repair_stats[fault_type][scheme]["count"] += 1
                if success:
                    fault_repair_stats[fault_type][scheme]["successful"] += 1
    
    # 计算成功率
    for scheme, stats in repair_stats.items():
        if stats["count"] > 0:
            stats["success_rate"] = round(stats["successful"] / stats["count"] * 100, 1)
    
    # 计算按故障类型的成功率
    for fault_type, schemes in fault_repair_stats.items():
        for scheme, stats in schemes.items():
            if stats["count"] > 0:
                stats["success_rate"] = round(stats["successful"] / stats["count"] * 100, 1)
    
    return {
        "overall": dict(repair_stats),
        "by_fault_type": dict(fault_repair_stats)
    }


def get_fault_summary(days=30):
    """获取故障统计摘要"""
    fault_history = load_fault_history()
    repair_history = load_repair_history()
    
    # 计算日期范围
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # 统计故障总数
    total_faults = 0
    fault_type_count = defaultdict(int)
    for record in fault_history:
        record_date = datetime.fromisoformat(record["timestamp"])
        if start_date <= record_date <= end_date:
            total_faults += 1
            fault_type_count[record["fault_type"]] += 1
    
    # 统计修复总数
    total_repairs = 0
    successful_repairs = 0
    repair_scheme_count = defaultdict(int)
    for record in repair_history:
        record_date = datetime.fromisoformat(record["timestamp"])
        if start_date <= record_date <= end_date:
            total_repairs += 1
            repair_scheme_count[record["scheme"]] += 1
            if record["success"]:
                successful_repairs += 1
    
    # 计算修复成功率
    repair_success_rate = (successful_repairs / total_repairs * 100) if total_repairs > 0 else 0
    
    # 获取最常见故障类型
    most_common_fault = None
    if fault_type_count:
        most_common_fault = max(fault_type_count.items(), key=lambda x: x[1])[0]
    
    # 获取最有效的修复方案
    most_effective_scheme = None
    if repair_scheme_count:
        most_effective_scheme = max(repair_scheme_count.items(), key=lambda x: x[1])[0]
    
    return {
        "time_range": f"最近{days}天",
        "total_faults": total_faults,
        "total_repairs": total_repairs,
        "repair_success_rate": round(repair_success_rate, 1),
        "most_common_fault": most_common_fault,
        "most_effective_scheme": most_effective_scheme,
        "fault_type_count": dict(fault_type_count),
        "repair_scheme_count": dict(repair_scheme_count)
    }


def print_fault_analysis(days=30):
    """打印故障分析报告"""
    print("=" * 60)
    print("网络故障原因及修复效果分析")
    print("=" * 60)
    
    # 获取故障摘要
    summary = get_fault_summary(days)
    print(f"\n【统计时间范围】{summary['time_range']}")
    print("-" * 50)
    print(f"  故障总数: {summary['total_faults']} 次")
    print(f"  修复总数: {summary['total_repairs']} 次")
    print(f"  修复成功率: {summary['repair_success_rate']}%")
    
    if summary['most_common_fault']:
        fault_name = FAULT_TYPES.get(summary['most_common_fault'], "未知故障")
        print(f"  最常见故障: {fault_name} ({summary['fault_type_count'][summary['most_common_fault']]} 次)")
    
    if summary['most_effective_scheme']:
        scheme_name = REPAIR_SCHEMES.get(summary['most_effective_scheme'], "未知修复方案")
        print(f"  最常用修复方案: {scheme_name} ({summary['repair_scheme_count'][summary['most_effective_scheme']]} 次)")
    
    # 故障类型分布
    print("\n【故障类型分布】")
    print("-" * 50)
    fault_dist = analyze_fault_distribution(days)
    for fault_type, stats in sorted(fault_dist.items(), key=lambda x: x[1]['count'], reverse=True):
        print(f"  {stats['name']:<20} {stats['count']:>6} 次  平均延迟: {stats['avg_latency']:>5}ms")
    
    # 修复方案效果
    print("\n【修复方案效果】")
    print("-" * 50)
    repair_effect = analyze_repair_effectiveness(days)
    for scheme, stats in sorted(repair_effect['overall'].items(), key=lambda x: x[1]['success_rate'], reverse=True):
        print(f"  {stats['name']:<20} 成功率: {stats['success_rate']:>5}%  ({stats['successful']}/{stats['count']} 次)")
    
    # 最近故障记录
    print("\n【最近故障记录】")
    print("-" * 50)
    fault_history = load_fault_history()
    recent_faults = sorted(fault_history, key=lambda x: x['timestamp'], reverse=True)[:5]
    for i, fault in enumerate(recent_faults, 1):
        timestamp = datetime.fromisoformat(fault['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
        print(f"  {i}. {timestamp} - {fault['fault_name']}")
        if fault['details']:
            for key, value in fault['details'].items():
                print(f"     {key}: {value}")
    
    # 最近修复记录
    print("\n【最近修复记录】")
    print("-" * 50)
    repair_history = load_repair_history()
    recent_repairs = sorted(repair_history, key=lambda x: x['timestamp'], reverse=True)[:5]
    for i, repair in enumerate(recent_repairs, 1):
        timestamp = datetime.fromisoformat(repair['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
        status = "成功" if repair['success'] else "失败"
        print(f"  {i}. {timestamp} - {repair['scheme_name']} - {status}")
        if repair['details']:
            for key, value in repair['details'].items():
                print(f"     {key}: {value}")
    
    print("\n" + "=" * 60)
    print("故障分析报告完成")
    print("=" * 60)


def run():
    """运行故障分析功能"""
    print_fault_analysis()
    
    # 返回分析结果
    return {
        "success": True,
        "summary": get_fault_summary(),
        "fault_distribution": analyze_fault_distribution(),
        "repair_effectiveness": analyze_repair_effectiveness(),
        "trends": analyze_fault_trends()
    }


if __name__ == "__main__":
    run()
