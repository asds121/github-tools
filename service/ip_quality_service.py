#!/usr/bin/env python3
"""IP质量服务 - 复杂的IP质量数据库管理和分析"""
import json
import time
from pathlib import Path

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Import from trace layer
from trace import fault_analysis

# Import from subprojects
from github_utils.common_utils import load_module

ROOT_DIR = Path(__file__).resolve().parent.parent

def load_ip_quality_db():
    """加载IP质量数据库"""
    ip_quality_db_path = ROOT_DIR / "trace" / "ip_quality_db.json"
    try:
        if ip_quality_db_path.exists():
            return json.loads(ip_quality_db_path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}

def save_ip_quality_db(db):
    """保存IP质量数据库"""
    ip_quality_db_path = ROOT_DIR / "trace" / "ip_quality_db.json"
    try:
        ip_quality_db_path.write_text(
            json.dumps(db, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        return True
    except Exception:
        return False

def analyze_ip_quality(ip, latency, success):
    """分析单个IP的质量并更新数据库"""
    db = load_ip_quality_db()
    
    if ip not in db:
        db[ip] = {
            "count": 0,
            "total_latency": 0,
            "success_count": 0,
            "last_updated": time.time(),
            "history": []
        }
    
    # 更新IP数据
    db[ip]["count"] += 1
    if latency is not None:
        db[ip]["total_latency"] += latency
    if success:
        db[ip]["success_count"] += 1
    db[ip]["last_updated"] = time.time()
    
    # 添加历史记录
    history_entry = {
        "timestamp": time.time(),
        "latency": latency,
        "success": success
    }
    db[ip]["history"].append(history_entry)
    
    # 只保留最近50条历史记录
    if len(db[ip]["history"]) > 50:
        db[ip]["history"] = db[ip]["history"][-50:]
    
    # 保存数据库
    save_ip_quality_db(db)
    
    return db[ip]

def get_top_ips(count=5):
    """获取质量排名前N的IP"""
    db = load_ip_quality_db()
    
    # 过滤掉测试次数不足的IP
    eligible_ips = [ip for ip, data in db.items() if data["count"] >= 3]
    
    # 按成功率和平均延迟排序
    sorted_ips = sorted(
        eligible_ips,
        key=lambda ip: (
            -db[ip]["success_count"] / db[ip]["count"],
            db[ip]["total_latency"] / db[ip]["count"]
        )
    )
    
    return sorted_ips[:count]

def get_ip_quality_report(ip):
    """生成单个IP的质量报告"""
    db = load_ip_quality_db()
    
    if ip not in db:
        return {
            "ip": ip,
            "exists": False,
            "message": "该IP尚未有测试记录"
        }
    
    data = db[ip]
    success_rate = data["success_count"] / data["count"] * 100
    avg_latency = data["total_latency"] / data["count"] if data["count"] > 0 else 0
    
    # 生成历史趋势数据
    recent_history = data["history"][-10:]
    history_trend = [{
        "timestamp": entry["timestamp"],
        "latency": entry["latency"],
        "success": entry["success"]
    } for entry in recent_history]
    
    return {
        "ip": ip,
        "exists": True,
        "test_count": data["count"],
        "success_count": data["success_count"],
        "success_rate": round(success_rate, 1),
        "avg_latency": round(avg_latency, 1),
        "last_updated": data["last_updated"],
        "history_trend": history_trend
    }

def generate_quality_report():
    """生成完整的IP质量报告"""
    db = load_ip_quality_db()
    
    # 计算整体统计信息
    total_ips = len(db)
    total_tests = sum(data["count"] for data in db.values())
    total_success = sum(data["success_count"] for data in db.values())
    avg_success_rate = total_success / total_tests * 100 if total_tests > 0 else 0
    
    # 获取质量最好的IP
    top_ips = get_top_ips(10)
    top_ip_reports = [get_ip_quality_report(ip) for ip in top_ips]
    
    # 生成报告
    report = {
        "generated_at": time.time(),
        "total_ips": total_ips,
        "total_tests": total_tests,
        "total_success": total_success,
        "avg_success_rate": round(avg_success_rate, 1),
        "top_ips": top_ip_reports,
        "ip_count_by_success_rate": {
            "excellent": len([ip for ip, data in db.items() if data["success_count"] / data["count"] > 0.9]),
            "good": len([ip for ip, data in db.items() if 0.7 <= data["success_count"] / data["count"] <= 0.9]),
            "average": len([ip for ip, data in db.items() if 0.5 <= data["success_count"] / data["count"] < 0.7]),
            "poor": len([ip for ip, data in db.items() if data["success_count"] / data["count"] < 0.5])
        }
    }
    
    return report

def cleanup_old_records(days=30):
    """清理旧的IP质量记录"""
    db = load_ip_quality_db()
    cutoff_time = time.time() - (days * 24 * 3600)
    
    # 删除超过指定天数未更新的记录
    old_ips = [ip for ip, data in db.items() if data["last_updated"] < cutoff_time]
    for ip in old_ips:
        del db[ip]
    
    # 保存清理后的数据库
    save_ip_quality_db(db)
    
    return len(old_ips)

def optimize_ip_quality_db():
    """优化IP质量数据库，减少冗余数据"""
    db = load_ip_quality_db()
    
    # 对每个IP的历史记录进行优化
    for ip, data in db.items():
        # 只保留最近100条历史记录
        if len(data.get("history", [])) > 100:
            data["history"] = data["history"][-100:]
        
        # 移除不再使用的字段
        for field in ["some_old_field", "deprecated_field"]:
            if field in data:
                del data[field]
    
    # 保存优化后的数据库
    save_ip_quality_db(db)
    
    return True

def run_ip_quality_analysis():
    """运行完整的IP质量分析"""
    print("开始IP质量分析...")
    
    # 生成质量报告
    report = generate_quality_report()
    
    # 清理旧记录
    old_records_deleted = cleanup_old_records()
    
    # 优化数据库
    optimize_ip_quality_db()
    
    # 记录分析结果
    fault_analysis.log_repair(
        scheme="ip_quality_analysis",
        success=True,
        details={
            "total_ips": report["total_ips"],
            "total_tests": report["total_tests"],
            "avg_success_rate": report["avg_success_rate"],
            "old_records_deleted": old_records_deleted,
            "top_ips": [ip["ip"] for ip in report["top_ips"]]
        }
    )
    
    print(f"IP质量分析完成:")
    print(f"- 总IP数: {report['total_ips']}")
    print(f"- 总测试数: {report['total_tests']}")
    print(f"- 平均成功率: {report['avg_success_rate']}%")
    print(f"- 删除旧记录: {old_records_deleted}条")
    print(f"- 质量最好的IP: {', '.join([ip['ip'] for ip in report['top_ips'][:3]])}")
    
    return report

# 直接运行时的入口
if __name__ == "__main__":
    run_ip_quality_analysis()
