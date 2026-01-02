#!/usr/bin/env python3
"""IP质量数据库 - 基础IP质量数据管理"""
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
IP_QUALITY_DB = ROOT_DIR / "trace" / "ip_quality_db.json"
IP_BLACKLIST = ROOT_DIR / "trace" / "ip_blacklist.json"


def load_ip_quality_db():
    """加载IP质量数据库"""
    try:
        if IP_QUALITY_DB.exists():
            return json.loads(IP_QUALITY_DB.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}



def save_ip_quality_db(db):
    """保存IP质量数据库"""
    try:
        IP_QUALITY_DB.write_text(json.dumps(db, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        print(f"保存IP质量库失败: {e}")



def record_ip_result(ip, latency, success):
    """记录单个IP的测试结果"""
    db = load_ip_quality_db()
    if ip not in db:
        db[ip] = {
            "count": 0, 
            "total_latency": 0, 
            "success_count": 0, 
            "last_success": None,
            "last_test_time": None
        }
    db[ip]["count"] += 1
    db[ip]["last_test_time"] = "now"  # 实际使用时应该记录时间戳
    
    if latency is not None:
        db[ip]["total_latency"] += latency
    
    if success:
        db[ip]["success_count"] += 1
        db[ip]["last_success"] = True
    else:
        db[ip]["last_success"] = False
    
    save_ip_quality_db(db)
    return db



def get_ip_quality(ip):
    """获取单个IP的质量信息"""
    db = load_ip_quality_db()
    return db.get(ip)



def load_blacklist():
    """加载IP黑名单"""
    try:
        if IP_BLACKLIST.exists():
            return json.loads(IP_BLACKLIST.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {"ips": [], "reasons": {}}



def save_blacklist(blacklist):
    """保存IP黑名单"""
    try:
        IP_BLACKLIST.write_text(json.dumps(blacklist, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        print(f"保存黑名单失败: {e}")



def add_to_blacklist(ip, reason="timeout"):
    """将IP加入黑名单"""
    blacklist = load_blacklist()
    if ip not in blacklist["ips"]:
        blacklist["ips"].append(ip)
    blacklist["reasons"][ip] = reason
    save_blacklist(blacklist)
    return blacklist



def remove_from_blacklist(ip):
    """从黑名单移除IP"""
    blacklist = load_blacklist()
    if ip in blacklist["ips"]:
        blacklist["ips"].remove(ip)
        blacklist["reasons"].pop(ip, None)
    save_blacklist(blacklist)
    return blacklist



def is_blacklisted(ip):
    """检查IP是否在黑名单"""
    blacklist = load_blacklist()
    return ip in blacklist["ips"]



def get_blacklisted_ips():
    """获取所有黑名单IP"""
    blacklist = load_blacklist()
    return blacklist["ips"]



def filter_blacklisted_ips(ips):
    """过滤掉黑名单中的IP"""
    return [ip for ip in ips if not is_blacklisted(ip)]


# 直接运行时的入口
if __name__ == "__main__":
    print("IP质量数据库基础功能")
    print("可用函数:")
    print("- load_ip_quality_db() - 加载IP质量数据库")
    print("- save_ip_quality_db(db) - 保存IP质量数据库")
    print("- record_ip_result(ip, latency, success) - 记录单个IP的测试结果")
    print("- get_ip_quality(ip) - 获取单个IP的质量信息")
    print("- load_blacklist() - 加载IP黑名单")
    print("- save_blacklist(blacklist) - 保存IP黑名单")
    print("- add_to_blacklist(ip, reason) - 将IP加入黑名单")
    print("- remove_from_blacklist(ip) - 从黑名单移除IP")
    print("- is_blacklisted(ip) - 检查IP是否在黑名单")
    print("- get_blacklisted_ips() - 获取所有黑名单IP")
    print("- filter_blacklisted_ips(ips) - 过滤掉黑名单中的IP")
