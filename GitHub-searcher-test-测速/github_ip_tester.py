#!/usr/bin/env python3
"""GitHub IP测速 - 测试访问GitHub首页速度"""
import socket
import sys
import json
import time
from pathlib import Path

# 直接读取本地配置文件
CONFIG_PATH = Path(__file__).resolve().parent / "config.json"
if CONFIG_PATH.exists():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        CONFIG = json.load(f)
    IPS = CONFIG["ips"]
    TIMEOUT = CONFIG["timeout"]
else:
    # 默认配置
    IPS = ["140.82.113.4", "140.82.114.4", "140.82.113.3"]
    TIMEOUT = 3

# 不使用共享数据库
USE_SHARED_DB = False


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
        return {"ip": ip, "latency": None, "status": "FAIL", "error": "timeout"}
    except Exception as e:
        return {"ip": ip, "latency": None, "status": "FAIL", "error": str(e)}


def test_all(ips=None, host="github.com", port=443):
    """测试所有IP并返回排序结果"""
    ips = ips or IPS
    
    results = []
    for ip in ips:
        result = test_homepage_speed(ip, host, port)
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
