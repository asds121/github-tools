#!/usr/bin/env python3
"""GitHub IP测速 - 测试访问GitHub首页速度"""
import socket
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from github_utils import load_sub_config

CONFIG = load_sub_config("GitHub-searcher-test-测速")

IPS = CONFIG["ips"]
TIMEOUT = CONFIG["timeout"]

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "trace"))
from ip_quality_db import record_ip_result, filter_blacklisted_ips
USE_SHARED_DB = True


def test_homepage_speed(ip, host="github.com", port=443, timeout=None):
    """测试访问GitHub首页的实际速度"""
    timeout = timeout or TIMEOUT
    start = time.time()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((ip, port))

        request = f"GET / HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
        s.sendall(request.encode())

        response = b""
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            response += chunk
            if time.time() - start > timeout:
                break

        s.close()
        latency = int((time.time() - start) * 1000)
        return {"ip": ip, "latency": latency, "status": "OK"}
    except socket.timeout:
        record_ip_result(ip, None, False)
        return {"ip": ip, "latency": None, "status": "FAIL", "error": "timeout"}
    except Exception as e:
        record_ip_result(ip, None, False)
        return {"ip": ip, "latency": None, "status": "FAIL", "error": str(e)}


def test_all(ips=None, host="github.com", port=443):
    """测试所有IP并返回排序结果"""
    ips = ips or IPS
    
    if USE_SHARED_DB:
        ips = filter_blacklisted_ips(ips)
    
    results = []
    for ip in ips:
        result = test_homepage_speed(ip, host, port)
        if result.get("latency"):
            record_ip_result(ip, result["latency"], True)
        results.append(result)
    results.sort(key=lambda x: x["latency"] or 9999)
    return results


def main():
    results = test_all()
    for r in results:
        if r["latency"]:
            print(f"{r['ip']:<18} {r['latency']}ms")
        else:
            print(f"{r['ip']:<18} FAIL")
    return results


if __name__ == "__main__":
    main()
