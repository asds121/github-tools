#!/usr/bin/env python3
"""GitHub守护进程 - 监控并维护GitHub连接状态"""
import sys
import time
import signal
from .config_utils import load_config
from .guardian_utils import (
    save_state, load_state, is_admin,
    find_best_ip, check_connection, get_current_hosts_github_ip,
    update_hosts
)


# 加载配置
CONFIG = load_config()
IP_POOL = CONFIG["ip_pool"]
CHECK_INTERVAL = CONFIG["check_interval"]
TIMEOUT = CONFIG["timeout"]

running = True


def check_and_repair(force=False):
    """检查连接状态并自动修复"""
    current_ip = get_current_hosts_github_ip()
    state = load_state()

    if not force and state:
        saved_ip = state.get("ip")
        saved_time = state.get("time", 0)
        if saved_ip == current_ip and time.time() - saved_time < CHECK_INTERVAL:
            return {"status": "cached", "ip": current_ip, "message": "使用缓存状态"}

    if check_connection(IP_POOL, TIMEOUT):
        last_status = {"status": "ok", "ip": current_ip, "time": time.time()}
        save_state(last_status)
        return {"status": "OK", "ip": current_ip, "message": "连接正常"}

    if not is_admin():
        return {"status": "FAIL", "ip": None, "error": "需要管理员权限"}

    ip = find_best_ip(IP_POOL, TIMEOUT)
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
        result = check_and_repair(True)
        print(f"状态: {result['status']}")
        if result.get('ip'):
            print(f"IP: {result['ip']}")
        if result.get('error'):
            print(f"错误: {result['error']}")


if __name__ == "__main__":
    main()
