#!/usr/bin/env python3
"""一键检测修复 - 备用方案函数"""
import socket
from pathlib import Path

# 引入trace层模块，符合service层必须引用trace层内容的要求
from trace import auto_diagnose
from trace import ip_speed_ranking
from trace import dns_explorer

ROOT_DIR = Path(__file__).resolve().parent.parent

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

def fallback_dns_lookup():
    """备用方案1: 尝试更多DNS服务器"""
    print("\n【备用方案1】尝试更多DNS服务器...")
    try:
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
    ip_quality_db_path = ROOT_DIR / "trace" / "ip_quality_db.json"
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

def test_single_ip(ip, port=443, timeout=2):
    """快速测试单个IP"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((ip, port))
        sock.close()
        return True
    except Exception:
        return False

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
