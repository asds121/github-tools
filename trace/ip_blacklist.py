#!/usr/bin/env python3
"""IP 黑名单 - 管理被排除的问题 IP，提高测速效率"""
import json
from datetime import datetime
from pathlib import Path

BLACKLIST_PATH = Path(__file__).parent / "ip_blacklist.json"

REASON_MAP = {
    "timeout": "连续超时",
    "slow": "延迟过高",
    "unstable": "不稳定"
}

DEFAULT_THRESHOLDS = {
    "timeout_count": 2,
    "slow_latency": 500,
    "slow_count": 3,
    "unstable_count": 5,
    "unstable_variance": 100
}


def load_blacklist():
    """加载黑名单"""
    if BLACKLIST_PATH.exists():
        try:
            return json.loads(BLACKLIST_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_blacklist(blacklist):
    """保存黑名单"""
    BLACKLIST_PATH.write_text(
        json.dumps(blacklist, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def add_to_blacklist(ip, reason, detail=""):
    """添加 IP 到黑名单"""
    blacklist = load_blacklist()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    blacklist[ip] = {
        "reason": reason,
        "detail": detail,
        "added_at": now
    }
    save_blacklist(blacklist)
    return True


def remove_from_blacklist(ip):
    """从黑名单移除 IP"""
    blacklist = load_blacklist()
    if ip in blacklist:
        del blacklist[ip]
        save_blacklist(blacklist)
        return True
    return False


def clear_blacklist():
    """清空黑名单"""
    BLACKLIST_PATH.write_text("{}", encoding="utf-8")
    return True


def get_blacklist():
    """获取黑名单"""
    return load_blacklist()


def check_and_add_to_blacklist(ip, test_results, thresholds=None):
    """检查 IP 是否应该加入黑名单"""
    thresholds = thresholds or DEFAULT_THRESHOLDS

    timeout_count = test_results.get("timeout_count", 0)
    latencies = test_results.get("latencies", [])
    latency_count = len(latencies)
    slow_count = sum(1 for latency in latencies if latency > thresholds["slow_latency"]) if latencies else 0

    if latency_count > 1:
        variance = sum((latency - sum(latencies)/len(latencies))**2 for latency in latencies) / len(latencies)
    else:
        variance = 0

    reasons = []
    if timeout_count >= thresholds["timeout_count"]:
        reasons.append(("timeout", f"连续 {timeout_count} 次超时"))

    if slow_count >= thresholds["slow_count"]:
        reasons.append(("slow", f"连续 {slow_count} 次延迟 > {thresholds['slow_latency']}ms"))

    if variance > thresholds["unstable_variance"] and latency_count >= thresholds["unstable_count"]:
        reasons.append(("unstable", f"延迟波动大，方差 {variance:.1f}"))

    if reasons:
        primary_reason, detail = reasons[0]
        add_to_blacklist(ip, primary_reason, detail)
        return True, primary_reason

    return False, None


def filter_blacklist(ips):
    """过滤掉黑名单中的 IP"""
    blacklist = load_blacklist()
    return [ip for ip in ips if ip not in blacklist]


def format_blacklist():
    """格式化输出黑名单"""
    blacklist = load_blacklist()
    if not blacklist:
        return "黑名单为空"

    lines = []
    for ip, info in sorted(blacklist.items()):
        reason = info.get("reason", "未知")
        added_at = info.get("added_at", "")
        reason_text = REASON_MAP.get(reason, reason)
        lines.append(f"  {ip:<20} {reason_text:<10} {added_at}")

    return "\n".join(lines)


def run():
    print("=" * 60)
    print("GitHub IP 黑名单管理")
    print("=" * 60)

    blacklist = load_blacklist()
    count = len(blacklist)

    print(f"\n【黑名单 IP】(共 {count} 个)")
    print("-" * 50)

    if blacklist:
        for ip, info in sorted(blacklist.items()):
            reason = info.get("reason", "未知")
            added_at = info.get("added_at", "")
            reason_text = REASON_MAP.get(reason, reason)
            print(f"  {ip:<18} {reason_text:<8} {added_at}")
    else:
        print("  黑名单为空")

    print("\n【操作】")
    print("-" * 50)
    print("  [1] 添加 IP 到黑名单")
    print("  [2] 从黑名单移除 IP")
    print("  [3] 清空黑名单")
    print("  [4] 导出黑名单")
    print("  [5] 刷新列表")

    print(f"  本次测速将跳过 {count} 个 IP")
    print()

    return blacklist


if __name__ == "__main__":
    run()
