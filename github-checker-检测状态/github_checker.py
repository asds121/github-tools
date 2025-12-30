# -*- coding: ascii -*-
"""
GitHub Checker v2.0.0 - Simple GitHub accessibility checker
"""

import sys
import time
import threading
from queue import Queue
import urllib.request

TARGETS = [
    ("homepage", "https://github.com"),
    ("api", "https://api.github.com"),
]
DEFAULT_TIMEOUT = 8.0
THRESHOLD_MS = 3000


def test_url(url, timeout):
    try:
        start = time.time()
        req = urllib.request.Request(url, headers={"User-Agent": "GitHubChecker/2.0"})
        r = urllib.request.urlopen(req, timeout=timeout)
        r.read()
        ms = round((time.time() - start) * 1000)
        return {"ok": r.status == 200, "ms": ms}
    except:
        return {"ok": False, "ms": 0}


def progress_bar(stop_event, queue):
    duration = DEFAULT_TIMEOUT
    start_time = time.time()
    chars = "|/-\\"
    i = 0
    while not stop_event.is_set():
        elapsed = time.time() - start_time
        percent = min(elapsed / duration * 100, 100)
        char = chars[i % len(chars)]
        sys.stdout.write(f"\r[{char}] Working... {percent:3.0f}%")
        sys.stdout.flush()
        i += 1
        time.sleep(0.1)
    queue.put(time.time() - start_time)


def run_with_progress(check_func):
    stop_event = threading.Event()
    queue = Queue()

    t = threading.Thread(target=progress_bar, args=(stop_event, queue))
    t.start()

    result = check_func()

    stop_event.set()
    t.join()

    return result


def check_single():
    results = []
    for name, url in TARGETS:
        results.append((name, test_url(url, DEFAULT_TIMEOUT)))
        if name == "homepage" and not results[-1][1]["ok"]:
            break

    avg_ms = sum(r[1]["ms"] for r in results) / len(results)

    if all(r[1]["ok"] for r in results):
        status = "good" if avg_ms < THRESHOLD_MS else "warn"
    else:
        status = "bad"

    return {"status": status, "ms": avg_ms, "results": results}


def check(timeout=DEFAULT_TIMEOUT):
    return run_with_progress(check_single)


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
