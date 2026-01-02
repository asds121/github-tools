#!/usr/bin/env python3
"""故障分析服务 - 复杂的故障分析和报告生成功能"""
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

# 导入trace层的基础功能
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from trace import fault_analysis

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

def analyze_fault_trends(days=30):
    """分析故障趋势"""
    fault_history = fault_analysis.load_fault_history()
    repair_history = fault_analysis.load_repair_history()
    
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
    fault_history = fault_analysis.load_fault_history()
    
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
    repair_history = fault_analysis.load_repair_history()
    
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
    fault_history = fault_analysis.load_fault_history()
    repair_history = fault_analysis.load_repair_history()
    
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
    fault_history = fault_analysis.load_fault_history()
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
    repair_history = fault_analysis.load_repair_history()
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

def generate_repair_report(repair_id=None, format="text"):
    """生成详细的修复报告
    
    Args:
        repair_id: 修复记录ID，None表示生成所有修复记录报告
        format: 报告格式，支持"text"和"json"
    
    Returns:
        生成的修复报告
    """
    repair_history = fault_analysis.load_repair_history()
    
    if repair_id:
        # 生成单个修复记录报告
        repair_record = next((r for r in repair_history if r.get("id") == repair_id), None)
        if not repair_record:
            return f"找不到ID为{repair_id}的修复记录"
        repair_records = [repair_record]
    else:
        # 生成所有修复记录报告，按时间倒序排序
        repair_records = sorted(repair_history, key=lambda x: x['timestamp'], reverse=True)
    
    if format == "json":
        # JSON格式报告
        report = {
            "generated_at": datetime.now().isoformat(),
            "repair_count": len(repair_records),
            "repair_records": repair_records
        }
        return json.dumps(report, ensure_ascii=False, indent=2)
    else:
        # 文本格式报告
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("GitHub连接修复详细报告")
        report_lines.append("=" * 80)
        report_lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"修复记录数量: {len(repair_records)}")
        report_lines.append("=" * 80)
        
        for i, record in enumerate(repair_records, 1):
            report_lines.append("")
            report_lines.append(f"修复记录 #{i}")
            report_lines.append("-" * 80)
            
            # 修复基本信息
            timestamp = datetime.fromisoformat(record["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
            report_lines.append(f"修复时间: {timestamp}")
            report_lines.append(f"修复方案: {record['scheme_name']} ({record['scheme']})")
            report_lines.append(f"修复状态: {'成功' if record['success'] else '失败'}")
            
            if record['fault_type']:
                fault_name = FAULT_TYPES.get(record['fault_type'], "未知故障")
                report_lines.append(f"故障类型: {fault_name} ({record['fault_type']})")
            
            # 详细修复信息
            report_lines.append("")
            report_lines.append("详细信息:")
            
            # 从details中提取更多信息
            details = record.get("details", {})
            
            # 修复原因
            report_lines.append(f"  修复原因: {details.get('reason', '未明确')}")
            
            # 修复方法
            report_lines.append(f"  修复方法: {details.get('fix_method', '未记录')}")
            
            # 验证结果
            report_lines.append(f"  验证结果: {details.get('verification', '未验证')}")
            
            # 修复策略
            if details.get('strategy'):
                report_lines.append(f"  修复策略: {details['strategy']}")
            
            # 网络环境信息
            if details.get('network_env'):
                network_env = details['network_env']
                report_lines.append(f"  网络环境: 可用IP数={network_env.get('available_ips_count', 'N/A')}, "
                                  f"当前延迟={network_env.get('current_latency', 'N/A')}ms, "
                                  f"DNS可用={'是' if network_env.get('dns_available') else '否'}")
            
            # 修复前后状态对比
            if 'before' in details and 'after' in details:
                report_lines.append(f"  修复前: {details['before']}")
                report_lines.append(f"  修复后: {details['after']}")
            
            # 其他详细信息
            for key, value in details.items():
                if key not in ['reason', 'fix_method', 'verification', 'strategy', 'network_env', 'before', 'after']:
                    report_lines.append(f"  {key}: {value}")
        
        report_lines.append("")
        report_lines.append("=" * 80)
        report_lines.append("报告结束")
        report_lines.append("=" * 80)
        
        return "\n".join(report_lines)

def save_repair_report(file_path, repair_id=None, format="text"):
    """保存修复报告到文件
    
    Args:
        file_path: 报告文件路径
        repair_id: 修复记录ID，None表示生成所有修复记录报告
        format: 报告格式，支持"text"和"json"
    
    Returns:
        保存结果
    """
    try:
        report = generate_repair_report(repair_id, format)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(report)
        return f"修复报告已保存到: {file_path}"
    except Exception as e:
        return f"保存修复报告失败: {str(e)}"

def run():
    """运行故障分析功能"""
    print_fault_analysis()
    
    # 返回分析结果
    return {
        "success": True,
        "summary": get_fault_summary(),
        "fault_distribution": analyze_fault_distribution(),
        "repair_effectiveness": analyze_repair_effectiveness(),
        "trends": analyze_fault_trends(),
        "report_generation": {
            "available_formats": ["text", "json"],
            "generate_report": "调用generate_repair_report()生成详细报告",
            "save_report": "调用save_repair_report()保存报告到文件"
        }
    }

if __name__ == "__main__":
    run()