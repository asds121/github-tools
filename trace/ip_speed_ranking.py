#!/usr/bin/env python3
"""IP 速度排行榜 - 多次测速并记录历史数据，筛选出长期稳定的优质 IP"""
import sys
import time
import statistics
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import importlib.util
from pathlib import Path

def load_module(module_path):
    """动态加载模块"""
    path = Path(module_path)
    spec = importlib.util.spec_from_file_location("tool_module", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

ROOT_DIR = Path(__file__).resolve().parent.parent

# 加载依赖模块
dns_module = load_module(
    ROOT_DIR / "GitHub-searcher-dns-DNS" / "github_dns.py"
)
get_dns_ips = dns_module.resolve_all

tester_module = load_module(
    ROOT_DIR / "GitHub-searcher-test-测速" / "github_ip_tester.py"
)
test_ips = tester_module.test_all

def calculate_score(latency, success_rate, variance):
    """计算 IP 综合评分"""
    # 权重配置
    WEIGHT_SUCCESS = 0.4
    WEIGHT_SPEED = 0.4
    WEIGHT_STABILITY = 0.2
    
    # 速度评分：越低越好，归一化到 0-100
    speed_score = max(0, 100 - (latency / 10))  # 1000ms 对应 0 分
    
    # 成功率评分：直接使用百分比
    success_score = success_rate * 100
    
    # 稳定度评分：方差越小越好，归一化到 0-100
    stability_score = max(0, 100 - (variance / 10))  # 1000ms 方差对应 0 分
    
    # 综合评分
    total_score = (
        WEIGHT_SUCCESS * success_score +
        WEIGHT_SPEED * speed_score +
        WEIGHT_STABILITY * stability_score
    )
    
    return round(total_score, 1)

def run():
    """运行 IP 速度排行榜功能"""
    print("=" * 60)
    print("GitHub IP 速度排行榜")
    print("=" * 60)
    
    # 配置参数
    TEST_ROUNDS = 3
    TEST_INTERVAL = 5  # 秒
    
    print(f"\n测试配置：{TEST_ROUNDS} 轮测速，间隔 {TEST_INTERVAL} 秒")
    print("=" * 60)
    
    # 第一步：解析 DNS 获取所有 IP 地址
    print("\n[1/5] 解析 DNS 获取 IP 列表...")
    ips = get_dns_ips()
    
    if not ips:
        print("  ✗ 无法解析 DNS，退出")
        return {"success": False, "message": "无法解析 DNS"}
    
    print(f"  ✓ 找到 {len(ips)} 个 IP 地址")
    
    # 第二步：执行多轮测速
    all_results = {}
    for round_num in range(TEST_ROUNDS):
        print(f"\n[2/{TEST_ROUNDS+1}] 第 {round_num+1} 轮测速...")
        
        results = test_ips(ips)
        
        # 保存本轮结果
        for r in results:
            ip = r["ip"]
            latency = r.get("latency")
            
            if ip not in all_results:
                all_results[ip] = {
                    "latencies": [],
                    "success_count": 0,
                    "total_count": 0
                }
            
            all_results[ip]["total_count"] += 1
            if latency:
                all_results[ip]["latencies"].append(latency)
                all_results[ip]["success_count"] += 1
        
        # 输出本轮最快 IP
        fastest = min(results, key=lambda x: x.get("latency", float("inf")))
        if fastest.get("latency"):
            print(f"  本轮最快: {fastest['ip']} ({fastest['latency']}ms)")
        
        # 间隔时间
        if round_num < TEST_ROUNDS - 1:
            print(f"  等待 {TEST_INTERVAL} 秒进行下一轮...")
            time.sleep(TEST_INTERVAL)
    
    # 第三步：计算统计数据
    print("\n[3/5] 计算统计数据...")
    ranking = []
    
    for ip, data in all_results.items():
        latencies = data["latencies"]
        success_count = data["success_count"]
        total_count = data["total_count"]
        
        if not latencies:
            continue
        
        # 计算统计指标
        avg_latency = statistics.mean(latencies)
        variance = statistics.variance(latencies) if len(latencies) > 1 else 0
        success_rate = success_count / total_count
        stability = 100 - (variance / 10)  # 转换为 0-100 分
        
        # 计算综合评分
        score = calculate_score(avg_latency, success_rate, variance)
        
        ranking.append({
            "ip": ip,
            "avg_latency": round(avg_latency),
            "success_rate": round(success_rate * 100),
            "stability": round(stability),
            "score": score
        })
    
    # 第四步：排序生成排行榜
    print("\n[4/5] 生成排行榜...")
    ranking.sort(key=lambda x: (-x["score"], x["avg_latency"]))
    
    # 输出排行榜
    print("\n" + "=" * 60)
    print("IP 地址          平均延迟    成功率    稳定度    综合评分")
    print("-" * 60)
    
    for item in ranking:
        print(f"{item['ip']:<18} {item['avg_latency']}ms      {item['success_rate']}%     {item['stability']}%       {item['score']}")
    
    # 第五步：生成稳定 IP 推荐
    print("\n" + "=" * 60)
    print("稳定 IP 推荐")
    print("-" * 60)
    
    # 筛选稳定 IP（成功率 100%，综合评分 > 80）
    stable_ips = [item for item in ranking if item["success_rate"] == 100 and item["score"] > 80]
    
    if stable_ips:
        print(f"共 {len(stable_ips)} 个稳定 IP，按评分排序：")
        print("\n# GitHub 稳定 IP（自动生成）")
        print(f"# 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"# 测试配置：{TEST_ROUNDS} 轮测速")
        
        for item in stable_ips:
            print(f"{item['ip']}    github.com")
            print(f"{item['ip']}    api.github.com")
    else:
        print("没有找到足够稳定的 IP")
    
    print("\n" + "=" * 60)
    print("IP 速度排行榜生成完成")
    print("=" * 60)
    
    return {
        "success": True,
        "ranking": ranking,
        "stable_ips": [item["ip"] for item in stable_ips],
        "test_rounds": TEST_ROUNDS
    }


if __name__ == "__main__":
    run()
