# -*- coding: ascii -*-
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


def test_connection(host, port, timeout):
    """Test connection using socket with real timeout control"""
    start = time.time()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((host, port))
        
        context = ssl.create_default_context()
        with s, context.wrap_socket(s, server_hostname=host) as ssock:
            request = f"GET / HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
            ssock.sendall(request.encode())
            ssock.recv(1024)
            
            ms = round((time.time() - start) * 1000)
            return {"ok": True, "ms": ms}
    except socket.timeout:
        return {"ok": False, "ms": 0, "error": "timeout"}
    except Exception as e:
        return {"ok": False, "ms": 0, "error": str(e)}


def check_single():
    results = []
    
    for name, host, port in TARGETS:
        # Start spinner using github_utils
        spinner = create_spinner()
        spinner_thread = spinner["start"]("Checking {host}... {char}", host=host)
        
        try:
            result = test_connection(host, port, DEFAULT_TIMEOUT)
        finally:
            spinner["stop"](spinner_thread)
        
        results.append((name, result))
        break

    homepage_result = results[0][1] if results else {"ok": False, "ms": 0}
    avg_ms = homepage_result["ms"]

    status = "good" if homepage_result["ok"] and avg_ms < 3000 else "warn" if homepage_result["ok"] else "bad"

    return {"status": status, "ms": avg_ms, "results": results}


def check(timeout=DEFAULT_TIMEOUT):
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
