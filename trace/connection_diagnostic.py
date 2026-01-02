#!/usr/bin/env python3
"""连接诊断 - 基础工具函数"""
import socket
import subprocess
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# 导入故障分析模块，用于记录故障信息
from trace import fault_analysis

ROOT_DIR = Path(__file__).resolve().parent.parent


def ping_host(host, count=1, timeout=2000):
    """ping 主机"""
    try:
        result = subprocess.run(
            ["ping", "-n", str(count), "-w", str(timeout), host],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except Exception:
        return False



def test_tcp_connectivity(host, port=443, timeout=5):
    """测试TCP连接，支持多个端口和超时设置"""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False



def test_multiple_ports(host, ports=(443, 80, 22), timeout=3):
    """测试多个端口的连接情况"""
    results = {}
    for port in ports:
        results[port] = test_tcp_connectivity(host, port, timeout)
    return results



def get_known_good_ips():
    """获取已知的可用IP列表"""
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
    try:
        dns_servers = ["8.8.8.8", "8.8.4.4", "1.1.1.1", "9.9.9.9", "208.67.222.222"]
        ips = []
        for server in dns_servers:
            try:
                import socket
                result = socket.gethostbyname_ex("github.com")
                for ip in result[2]:
                    if ip not in ips:
                        ips.append(ip)
            except Exception:
                continue
        return ips
    except Exception:
        pass
    return []



def fallback_known_ips():
    """备用方案2: 使用已知的可用IP"""
    return get_known_good_ips()



def fallback_ip_quality_db():
    """备用方案3: 使用IP质量数据库中的成功IP"""
    ip_quality_db_path = Path(__file__).resolve().parent / "ip_quality_db.json"
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
                    return [c[0] for c in candidates[:5]]
    except Exception:
        pass
    return []



def fallback_quick_test(ips):
    """备用方案4: 快速测试IP"""
    results = []
    for ip in ips[:10]:
        if test_single_ip(ip):
            results.append(ip)
    return results



def test_single_ip(ip, port=443, timeout=2):
    """快速测试单个IP"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((ip, port))
        sock.close()
        return True
    except Exception:
        return False



def fallback_manual_config():
    """备用方案5: 提供手动配置建议"""
    return {"manual": True}


def run(progress_callback=None):
    """连接诊断主函数 - 调用service层的复杂诊断逻辑"""
    try:
        # 调用service层的连接诊断服务
        from service import connection_diagnostic_service
        
        # 调用service层的run_diagnosis函数处理实际的诊断
        result = connection_diagnostic_service.run_diagnosis(progress_callback)
        
        return result
    except Exception as e:
        print(f"\n[错误] 调用连接诊断服务失败: {e}")
        print("[建议] 检查service层connection_diagnostic_service.py是否正确实现")
        return {"success": False, "message": f"调用诊断服务失败: {e}"}


# 直接运行时的入口
if __name__ == "__main__":
    print("GitHub连接诊断")
    result = run()
    print(f"诊断结果: {result}")
