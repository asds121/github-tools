# -*- coding: utf-8 -*-
"""
GitHub Checker v2.0.0 - Simple GitHub accessibility checker
"""

import time
import socket
import ssl
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from github_utils.common_utils import create_spinner

TARGETS = [
    ("homepage", "github.com", 443),
]
DEFAULT_TIMEOUT = 8.0


def test_connection(host, port, timeout, verify_ssl=True, retry=1):
    """Test connection using socket with real timeout control
    
    Args:
        host: Hostname or IP address to test
        port: Port number to connect to
        timeout: Connection timeout in seconds
        verify_ssl: Whether to verify SSL certificate
        retry: Number of retry attempts
    """
    for attempt in range(retry + 1):
        start = time.time()
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            s.connect((host, port))
            
            # 创建SSL上下文，根据verify_ssl参数决定是否严格验证证书
            context = ssl.create_default_context()
            if not verify_ssl:
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
            
            try:
                with s, context.wrap_socket(s, server_hostname=host) as ssock:
                    request = f"GET / HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
                    ssock.sendall(request.encode())
                    response = ssock.recv(1024)
                    
                    if response:
                        ms = round((time.time() - start) * 1000)
                        return {
                            "ok": True, 
                            "ms": ms,
                            "attempt": attempt + 1
                        }
                    else:
                        raise Exception("Empty response received")
            except ssl.SSLCertVerificationError as e:
                # SSL证书验证失败，但连接已建立，认为连接成功但记录证书问题
                ms = round((time.time() - start) * 1000)
                return {
                    "ok": True, 
                    "ms": ms, 
                    "warning": f"SSL certificate verification failed, but connection established: {str(e)}",
                    "attempt": attempt + 1
                }
            except ssl.SSLError as e:
                # 其他SSL错误
                if attempt < retry:
                    time.sleep(0.5)  # 等待0.5秒后重试
                    continue
                ms = round((time.time() - start) * 1000)
                return {
                    "ok": False, 
                    "ms": ms, 
                    "error": f"SSL error: {str(e)}",
                    "attempt": attempt + 1
                }
        except socket.timeout:
            if attempt < retry:
                time.sleep(0.5)  # 等待0.5秒后重试
                continue
            return {
                "ok": False, 
                "ms": 0, 
                "error": "timeout",
                "attempt": attempt + 1
            }
        except ConnectionResetError as e:
            if attempt < retry:
                time.sleep(0.5)  # 等待0.5秒后重试
                continue
            return {
                "ok": False, 
                "ms": 0, 
                "error": f"Connection reset: {str(e)}",
                "attempt": attempt + 1
            }
        except Exception as e:
            if attempt < retry:
                time.sleep(0.5)  # 等待0.5秒后重试
                continue
            return {
                "ok": False, 
                "ms": 0, 
                "error": str(e),
                "attempt": attempt + 1
            }
    
    # 如果所有重试都失败
    return {
        "ok": False, 
        "ms": 0, 
        "error": "All connection attempts failed",
        "attempt": retry + 1
    }


def check_single():
    results = []
    
    for name, host, port in TARGETS:
        # Start spinner using github_utils
        spinner = create_spinner()
        spinner_thread = spinner["start"]("Checking {host}... {char}", host=host)
        
        try:
            result = test_connection(host, port, DEFAULT_TIMEOUT, verify_ssl=True, retry=2)
        finally:
            spinner["stop"](spinner_thread)
        
        results.append((name, result))
        break

    homepage_result = results[0][1] if results else {"ok": False, "ms": 0}
    avg_ms = homepage_result["ms"]

    status = "good" if homepage_result["ok"] and avg_ms < 3000 else "warn" if homepage_result["ok"] else "bad"

    return {"status": status, "ms": avg_ms, "results": results}


def check(timeout=DEFAULT_TIMEOUT, verify_ssl=True):
    return check_single()


def main():
    r = check()
    status = r["status"].upper()
    suffix = f" ({r['ms']}ms)" if r["status"] != "bad" else ""
    print(f"\nStatus: {status}{suffix}")
    for name, res in r["results"]:
        print(f"  {name}: {'OK' if res['ok'] else 'FAIL'} ({res['ms']}ms)")


if __name__ == "__main__":
    main()
