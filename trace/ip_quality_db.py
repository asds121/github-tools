#!/usr/bin/env python3
"""IP质量数据库 - 模块间共享IP质量数据"""
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
        db[ip] = {"count": 0, "total_latency": 0, "success_count": 0, "last_success": None}
    db[ip]["count"] += 1
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


def get_good_ips(min_success_rate=0.5, min_count=2):
    """获取高质量IP列表"""
    db = load_ip_quality_db()
    good_ips = []
    for ip, data in db.items():
        if data.get("count", 0) >= min_count:
            success_rate = data.get("success_count", 0) / data.get("count", 1)
            if success_rate >= min_success_rate:
                avg_latency = data.get("total_latency", 0) / data.get("count", 1)
                good_ips.append((ip, avg_latency, success_rate))
    good_ips.sort(key=lambda x: (x[2], x[1]))
    return good_ips


def get_best_ip():
    """获取最佳IP"""
    good_ips = get_good_ips(min_success_rate=0.7, min_count=3)
    if good_ips:
        return good_ips[0][0]
    return None


def get_top_ips(limit=5):
    """获取Top N最佳IP"""
    good_ips = get_good_ips()
    return [ip for ip, latency, rate in good_ips[:limit]]


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


def get_statistics():
    """获取统计信息"""
    db = load_ip_quality_db()
    blacklist = load_blacklist()
    
    total_ips = len(db)
    good_count = len([ip for ip, data in db.items() 
                      if data.get("success_count", 0) / max(data.get("count", 1), 1) >= 0.5])
    bad_count = total_ips - good_count
    
    return {
        "total_ips": total_ips,
        "good_ips": good_count,
        "bad_ips": bad_count,
        "blacklist_count": len(blacklist.get("ips", [])),
        "db": db
    }


def export_known_good_ips():
    """导出已知可用的IP列表（用于配置文件）"""
    good_ips = get_good_ips(min_success_rate=0.8, min_count=3)
    config_ips = [ip for ip, _, _ in good_ips]
    
    if len(config_ips) < 5:
        default_ips = [
            "140.82.113.3",
            "140.82.114.3",
            "140.82.112.3",
            "140.82.114.4",
            "140.82.113.4",
            "20.205.243.166",
            "20.205.243.165",
        ]
        for ip in default_ips:
            if ip not in config_ips:
                config_ips.append(ip)
    
    return config_ips[:10]


if __name__ == "__main__":
    stats = get_statistics()
    print("=" * 50)
    print("IP质量数据库统计")
    print("=" * 50)
    print(f"总IP数: {stats['total_ips']}")
    print(f"优质IP: {stats['good_ips']}")
    print(f"问题IP: {stats['bad_ips']}")
    print(f"黑名单: {stats['blacklist_count']}")
    
    print("\n【Top 5 最佳IP】")
    top_ips = get_top_ips(5)
    for i, ip in enumerate(top_ips, 1):
        quality = get_ip_quality(ip)
        if quality:
            rate = quality["success_count"] / quality["count"] * 100
            avg = quality["total_latency"] / quality["count"]
            print(f"  {i}. {ip}: {rate:.0f}%成功率, 平均延迟{avg:.0f}ms")
    
    print("\n【黑名单IP】")
    blacklist = get_blacklisted_ips()
    if blacklist:
        for ip in blacklist[:10]:
            print(f"  - {ip}")
    else:
        print("  无")
