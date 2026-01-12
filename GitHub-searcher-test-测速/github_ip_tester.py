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


def test_homepage_speed(ip, host="github.com", port=443, timeout=None, retry=2):
    """测试访问GitHub首页的实际速度"""
    timeout = timeout or TIMEOUT
    import ssl
    
    for attempt in range(retry + 1):
        start = time.time()
        try:
            # 创建socket连接
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            s.connect((ip, port))

            # 添加SSL支持
            context = ssl.create_default_context()
            context.check_hostname = False  # 允许IP与hostname不匹配
            context.verify_mode = ssl.CERT_NONE  # 忽略证书验证
            
            with context.wrap_socket(s, server_hostname=host) as ssock:
                # 发送HTTP请求
                request = f"GET / HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
                ssock.sendall(request.encode())

                # 接收响应
                response = b""
                while True:
                    chunk = ssock.recv(4096)
                    if not chunk:
                        break
                    response += chunk
                    if b"HTTP/1.1 200 OK" in response:
                        break  # 只要收到200 OK就可以结束，不需要完整响应
                    if time.time() - start > timeout:
                        break

            latency = int((time.time() - start) * 1000)
            return {
                "ip": ip, 
                "latency": latency, 
                "status": "OK",
                "attempt": attempt + 1,
                "response_code": "200 OK" if b"HTTP/1.1 200 OK" in response else "Unknown"
            }
        except socket.timeout:
            if attempt < retry:
                time.sleep(0.5)
                continue
            return {
                "ip": ip, 
                "latency": None, 
                "status": "FAIL", 
                "error": "timeout",
                "attempt": attempt + 1
            }
        except ssl.SSLError as e:
            if attempt < retry:
                time.sleep(0.5)
                continue
            return {
                "ip": ip, 
                "latency": None, 
                "status": "FAIL", 
                "error": f"SSL error: {str(e)}",
                "attempt": attempt + 1
            }
        except ConnectionResetError as e:
            if attempt < retry:
                time.sleep(0.5)
                continue
            return {
                "ip": ip, 
                "latency": None, 
                "status": "FAIL", 
                "error": f"Connection reset: {str(e)}",
                "attempt": attempt + 1
            }
        except Exception as e:
            if attempt < retry:
                time.sleep(0.5)
                continue
            return {
                "ip": ip, 
                "latency": None, 
                "status": "FAIL", 
                "error": str(e),
                "attempt": attempt + 1
            }
    
    return {
        "ip": ip, 
        "latency": None, 
        "status": "FAIL", 
        "error": "All attempts failed",
        "attempt": retry + 1
    }


def test_all(ips=None, host="github.com", port=443):
    """测试所有IP并返回排序结果
    
    优化：先进行TCP连接预筛选，只对TCP连接成功的IP进行完整HTTP测速
    预期：IP测速时间减少30%，预筛选准确率≥85%
    """
    ips = ips or IPS
    
    # 1. TCP连接预筛选
    import socket
    
    def test_tcp(ip, port=443, timeout=1, retry=2):
        """快速测试TCP连接，带重试机制"""
        for attempt in range(retry + 1):
            try:
                with socket.create_connection((ip, port), timeout=timeout):
                    return True
            except socket.timeout:
                if attempt == retry:
                    return False
                time.sleep(0.2)  # 等待200ms后重试
            except Exception:
                if attempt == retry:
                    return False
                time.sleep(0.2)  # 等待200ms后重试
        return False
    
    # 并行测试TCP连接，提高筛选效率
    import concurrent.futures
    
    print(f"  开始TCP预筛选 {len(ips)} 个IP...")
    tcp_test_results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_ip = {executor.submit(test_tcp, ip, port, 1): ip for ip in ips}
        for future in concurrent.futures.as_completed(future_to_ip):
            ip = future_to_ip[future]
            try:
                tcp_test_results[ip] = future.result()
            except Exception:
                tcp_test_results[ip] = False
    
    # 筛选出TCP连接成功的IP
    tcp_available_ips = [ip for ip, success in tcp_test_results.items() if success]
    print(f"  TCP预筛选完成，{len(tcp_available_ips)}/{len(ips)} 个IP可用")
    
    # 2. 对TCP连接成功的IP进行完整HTTP测速
    results = []
    for ip in tcp_available_ips:
        result = test_homepage_speed(ip, host, port)
        results.append(result)
    
    # 3. 确保结果包含所有IP，TCP失败的IP标记为FAIL
    for ip in ips:
        if ip not in [r['ip'] for r in results]:
            results.append({"ip": ip, "latency": None, "status": "FAIL", "error": "TCP连接失败"})
    
    # 4. 智能排序算法：综合考虑延迟、成功率和响应质量
    def ip_quality_score(result):
        """计算IP质量评分（0-100）"""
        if result["status"] != "OK" or result["latency"] is None:
            return 0
        
        # 延迟评分：延迟越低，评分越高（40%权重）
        # 100ms以内：100分，超过1000ms：0分
        latency = result["latency"]
        latency_score = max(0, 100 - min(100, (latency - 100) / 9))
        
        # 响应质量评分：有200 OK响应的评分更高（30%权重）
        response_score = 100 if result.get("response_code") == "200 OK" else 70
        
        # 尝试次数评分：第一次尝试就成功的评分更高（30%权重）
        attempt = result.get("attempt", 1)
        attempt_score = max(0, 100 - (attempt - 1) * 30)
        
        # 综合评分
        total_score = (latency_score * 0.4) + (response_score * 0.3) + (attempt_score * 0.3)
        return total_score
    
    # 5. 为每个结果添加质量评分
    for result in results:
        result["quality_score"] = ip_quality_score(result)
    
    # 6. 排序：先按质量评分降序，再按延迟升序
    sorted_results = sorted(
        results,
        key=lambda x: (-x["quality_score"], x["latency"] if x["latency"] is not None else float("inf"))
    )
    
    # 7. 过滤：只返回质量评分>0的结果
    filtered_results = [r for r in sorted_results if r["quality_score"] > 0]
    
    # 8. 如果没有可用IP，返回所有结果
    if not filtered_results:
        filtered_results = sorted_results
    
    # 9. 最终排序：优先显示OK状态的IP，按延迟升序
    final_results = sorted(
        filtered_results,
        key=lambda x: (x["status"] != "OK", x["latency"] or float("inf"))
    )
    
    return final_results


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
