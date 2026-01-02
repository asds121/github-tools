#!/usr/bin/env python3
"""测试优化后的IP质量评估算法"""

from trace.ip_quality_db import (
    get_good_ips, get_best_ip, get_ip_detailed_quality, 
    calculate_ip_score, record_ip_result
)

def main():
    print('优化后的IP质量评估算法测试:')
    print('=' * 60)
    
    # 1. 测试get_good_ips函数
    print('\n1. 优质IP列表（按综合评分排序）:')
    good_ips = get_good_ips()
    if good_ips:
        for ip, latency, success_rate, consecutive, score in good_ips[:5]:
            print(f'   {ip}: 评分{score:.1f}, 延迟{latency:.0f}ms, 成功率{success_rate:.1%}, 连续成功{consecutive}次')
    else:
        print('   没有符合条件的优质IP')
    
    # 2. 测试get_best_ip函数
    print('\n2. 最佳IP:')
    best_ip = get_best_ip()
    if best_ip:
        print(f'   IP地址: {best_ip}')
        detailed_info = get_ip_detailed_quality(best_ip)
        if detailed_info:
            print(f'   详细信息:')
            for key, value in detailed_info.items():
                if key != 'ip':  # 已经显示过IP了
                    print(f'     {key}: {value}')
    else:
        print('   没有找到最佳IP')
    
    # 3. 测试评分计算示例
    print('\n3. 评分计算示例:')
    sample_data = {
        "count": 10, 
        "total_latency": 1000, 
        "success_count": 9, 
        "consecutive_success": 5
    }
    print(f'   示例数据: {sample_data}')
    score = calculate_ip_score(sample_data)
    print(f'   综合评分: {score:.1f}')
    
    # 4. 测试不同参数下的评分
    print('\n4. 不同参数下的评分测试:')
    test_cases = [
        {"name": "优秀IP", "data": {"count": 20, "total_latency": 2000, "success_count": 19, "consecutive_success": 10}},
        {"name": "良好IP", "data": {"count": 15, "total_latency": 4500, "success_count": 12, "consecutive_success": 5}},
        {"name": "一般IP", "data": {"count": 10, "total_latency": 8000, "success_count": 6, "consecutive_success": 2}},
        {"name": "较差IP", "data": {"count": 5, "total_latency": 5000, "success_count": 2, "consecutive_success": 0}},
    ]
    
    for test_case in test_cases:
        score = calculate_ip_score(test_case["data"])
        print(f'   {test_case["name"]}: 评分{score:.1f}')
    
    print('\n' + '=' * 60)
    print('IP质量评估算法测试完成!')

if __name__ == "__main__":
    main()
