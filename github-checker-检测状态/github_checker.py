# -*- coding: ascii -*-
"""
GitHub Checker v2.0.0 - Simple GitHub accessibility checker
"""

import sys
import time
import threading
from queue import Queue
import socket
import ssl
import urllib.request

TARGETS = [
    ("homepage", "github.com", 443),
    ("api", "api.github.com", 443),
]
DEFAULT_TIMEOUT = 8.0
THRESHOLD_MS = 3000


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
            response = ssock.recv(1024)
            
            ms = round((time.time() - start) * 1000)
            return {"ok": True, "ms": ms}
    except socket.timeout:
        return {"ok": False, "ms": 0, "error": "timeout"}
    except Exception as e:
        return {"ok": False, "ms": 0, "error": str(e)}


def test_url(url, timeout):
    """Backward compatibility interface"""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return test_connection(parsed.netloc, parsed.port or 443, timeout)
    except Exception:
        return {"ok": False, "ms": 0}


def progress_bar(stop_event, queue, output_func=None):
    duration = DEFAULT_TIMEOUT
    start_time = time.time()
    chars = "|/-\\"
    i = 0
    last_line = ""
    while not stop_event.is_set():
        elapsed = time.time() - start_time
        percent = min(elapsed / duration * 100, 100)
        char = chars[i % len(chars)]
        line = f"  [{char}] Working... {percent:3.0f}%"
        if output_func is None:
            sys.stdout.write(f"\r{line}")
            sys.stdout.flush()
            last_line = line
        else:
            output_func(line)
        i += 1
        time.sleep(0.1)
    if output_func is None:
        sys.stdout.write(" " * len(last_line) + "\r")
        sys.stdout.flush()
    queue.put(time.time() - start_time)


def run_with_progress(check_func, output_func=None):
    stop_event = threading.Event()
    queue = Queue()

    t = threading.Thread(target=progress_bar, args=(stop_event, queue, output_func))
    t.start()

    result = check_func()

    stop_event.set()
    t.join()

    return result


def check_single():
    results = []
    for name, host, port in TARGETS:
        result = test_connection(host, port, DEFAULT_TIMEOUT)
        results.append((name, result))
        if name == "homepage" and not result["ok"]:
            break

    avg_ms = sum(r[1]["ms"] for r in results if r[1]["ok"]) / len([r for r in results if r[1]["ok"]]) if [r for r in results if r[1]["ok"]] else 0

    if all(r[1]["ok"] for r in results):
        status = "good" if avg_ms < THRESHOLD_MS else "warn"
    else:
        status = "bad"

    return {"status": status, "ms": avg_ms, "results": results}


def check(timeout=DEFAULT_TIMEOUT, output_func=None):
    return run_with_progress(check_single, output_func)


def main():
    full = "--full" in sys.argv[1:] or "-f" in sys.argv[1:]

    if full:
        print("Full test (3 times)...")
        ok = 0
        for i in range(3):
            r = check()
            status = "OK" if r["status"] != "bad" else "FAIL"
            if r["status"] != "bad":
                ok += 1
            print(f"  #{i+1}: {status}")
        print(f"\nResult: {ok}/3 OK")
    else:
        r = check()
        status = r["status"].upper()
        suffix = f" ({r['ms']:.0f}ms)" if r["status"] != "bad" else ""
        print(f"\nStatus: {status}{suffix}")
        for name, res in r["results"]:
            print(f"  {name}: {'OK' if res['ok'] else 'FAIL'} ({res['ms']}ms)")


if __name__ == "__main__":
    main()
