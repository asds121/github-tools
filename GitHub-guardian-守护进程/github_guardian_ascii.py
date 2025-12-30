#!/usr/bin/env python3
"""GitHub守护进程 - 监控并维护GitHub连接状态"""
import os
import sys
import time
import socket
import signal
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from github_utils import load_sub_config

CONFIG = load_sub_config("GitHub-guardian-守护进程")

HOSTS_PATH = Path(os.environ.get("SystemRoot", "C:\\Windows")) / "System32" / "drivers" / "etc" / "hosts"
IP_POOL = CONFIG["ip_pool"]
CHECK_INTERVAL = CONFIG["check_interval"]
TIMEOUT = CONFIG["timeout"]

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "trace"))
try:
    from ip_quality_db import record_ip_result
    USE_SHARED_DB = True
except ImportError:
    USE_SHARED_DB = False

STATE_FILE = Path(__file__).resolve().parent.parent / "trace" / "guardian_state.json"

running = True
last_status = {"status": "unknown", "ip": None, "time": None}
state_lock = threading.Lock()


def save_state(state):
    """保存状态到文件"""
    with state_lock:
        try:
            STATE_FILE.write_text(
                __import__("json").dumps(state, ensure_ascii=False),
                encoding="utf-8"
            )
        except Exception:
            pass


def load_state():
    """加载上次状态"""
    try:
        if STATE_FILE.exists():
            return __import__("json").loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return None


def is_admin():
    """检查是否具有管理员权限"""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def test_connect(ip, port=443, timeout=None):
    """测试IP连接是否可达"""
    timeout = timeout or TIMEOUT
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((ip, port))
        s.close()
        return True
    except Exception:
        return False


def find_best_ip(ip_pool=None, timeout=None):
    """查找最佳的可用IP"""
    ip_pool = ip_pool or IP_POOL
    timeout = timeout or TIMEOUT
    best_ip = None
    for ip in ip_pool:
        if test_connect(ip, timeout=timeout):
            best_ip = ip
            if USE_SHARED_DB:
                record_ip_result(ip, timeout * 1000, True)
            break
        elif USE_SHARED_DB:
            record_ip_result(ip, None, False)
    return best_ip


def get_current_hosts_github_ip():
    """获取当前hosts中github.com的IP"""
    try:
        with open(HOSTS_PATH, "rb") as f:
            content = f.read().decode("gbk", errors="ignore")
        for line in content.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) >= 2 and parts[1] == "github.com":
                return parts[0]
    except Exception:
        pass
    return None


def update_hosts(ip, domains=None):
    """更新hosts文件"""
    if not ip:
        return {"success": False, "error": "未提供IP"}

    domains = domains or ["github.com", "api.github.com"]

    try:
        with open(HOSTS_PATH, "rb") as f:
            content = f.read().decode("gbk", errors="ignore")
        lines = [line for line in content.split("\n") if "github" not in line.lower() or "#" in line]
        for domain in domains:
            lines.append(f"{ip}    {domain}")
        with open(HOSTS_PATH, "wb") as f:
            f.write("\n".join(lines).encode("gbk"))
        os.system("ipconfig /flushdns")
        return {"success": True, "ip": ip}
    except Exception as e:
        return {"success": False, "error": str(e)}


def check_connection():
    """检查GitHub连接状态"""
    checker_module = __import__("sys").modules.get("github_checker")
    if checker_module is None:
        checker_path = Path(__file__).resolve().parent.parent / "github-checker-检测状态"
        sys.path.insert(0, str(checker_path))
        import github_checker as checker_module
    result = checker_module.check()
    return result["status"] != "bad"


def check_and_repair(force=False):
    """检查连接状态并自动修复"""
    current_ip = get_current_hosts_github_ip()
    state = load_state()

    if not force and state:
        saved_ip = state.get("ip")
        saved_time = state.get("time", 0)
        if saved_ip == current_ip and time.time() - saved_time < CHECK_INTERVAL:
            return {"status": "cached", "ip": current_ip, "message": "使用缓存状态"}

    if check_connection():
        last_status = {"status": "ok", "ip": current_ip, "time": time.time()}
        save_state(last_status)
        return {"status": "OK", "ip": current_ip, "message": "连接正常"}

    if not is_admin():
        return {"status": "FAIL", "ip": None, "error": "需要管理员权限"}

    ip = find_best_ip()
    if ip:
        result = update_hosts(ip)
        if result["success"]:
            last_status = {"status": "fixed", "ip": ip, "time": time.time()}
            save_state(last_status)
            return {"status": "OK", "ip": ip, "update": result, "message": "已修复"}
        return {"status": "FAIL", "ip": ip, "error": result.get("error", "更新失败")}
    else:
        return {"status": "FAIL", "ip": None, "error": "无可用IP"}


def signal_handler(signum, frame):
    """处理退出信号"""
    global running
    running = False


def guardian_loop():
    """守护进程主循环"""
    global running
    print("=" * 50)
    print("GitHub 守护进程已启动")
    print(f"检查间隔: {CHECK_INTERVAL}秒")
    print("按 Ctrl+C 退出")
    print("=" * 50)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    running = True

    while running:
        result = check_and_repair()
        if result["status"] == "OK":
            print(f"[{time.strftime('%H:%M:%S')}] 状态: 正常 (IP: {result.get('ip', 'N/A')})")
        elif result["status"] == "cached":
            print(f"[{time.strftime('%H:%M:%S')}] 状态: 缓存 (IP: {result.get('ip', 'N/A')})")
        elif result["status"] == "fixed":
            print(f"[{time.strftime('%H:%M:%S')}] 状态: 已修复 (IP: {result.get('ip', 'N/A')})")
        else:
            print(f"[{time.strftime('%H:%M:%S')}] 状态: 异常 - {result.get('error', '未知错误')}")

        for _ in range(CHECK_INTERVAL):
            if not running:
                break
            time.sleep(1)

    print("\n守护进程已退出")


def main():
    if "--daemon" in sys.argv[1:]:
        guardian_loop()
    else:
        result = check_and_repair()
        print(f"状态: {result['status']}")
        if result.get('ip'):
            print(f"IP: {result['ip']}")
        if result.get('error'):
            print(f"错误: {result['error']}")


if __name__ == "__main__":
    main()
