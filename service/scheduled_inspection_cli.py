#!/usr/bin/env python3
"""定时巡检 - 命令行交互模块"""
from datetime import datetime

# 引入trace层模块，符合service层必须引用trace层内容的要求
from trace import scheduled_inspection
from trace import data_statistics


def print_status(status):
    """打印巡检状态"""
    print("=" * 60)
    print("GitHub 定时巡检")
    print("=" * 60)
    
    # 输出当前配置
    print("\n【巡检设置】")
    print("-" * 50)
    print(f"巡检周期: 每 {status['interval']//60} 分钟")
    print(f"告警方式: {status['alert_method']}")
    print(f"历史数据保留: {status['retention_days']} 天")
    
    # 输出当前状态
    print("\n【当前状态】")
    print("-" * 50)
    print(f"巡检服务: {'运行中' if status['is_running'] else '已停止'}")
    
    if status['is_running'] and status['next_inspection']:
        next_time = status['next_inspection'].strftime("%H:%M:%S")
        print(f"下次巡检: {next_time}")
    
    # 输出今日统计
    stats = status['today_stats']
    print("\n【今日统计】")
    print("-" * 50)
    print(f"巡检次数:     {stats['count']}")
    print(f"正常次数:     {stats['normal']}")
    print(f"异常次数:     {stats['abnormal']}")
    print(f"平均延迟:     {stats['avg_latency']}ms")
    print(f"可用率:       {stats['availability']}%")
    
    # 输出最近异常
    recent_abnormal = status['recent_abnormal']
    if recent_abnormal:
        print("\n【最近异常】")
        print("-" * 50)
        for record in recent_abnormal:
            dt = datetime.fromisoformat(record["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
            print(f"时间: {dt}")
            print(f"原因: {record['message'] or '连接失败'}")
            print("-" * 30)
    
    # 输出操作选项
    print("\n【操作选项】")
    print("-" * 50)
    print("[1] 启动巡检")
    print("[2] 停止巡检")
    print("[3] 修改巡检周期")
    print("[4] 立即执行一次巡检")
    print("[5] 查看历史记录")


def print_inspection_result(record):
    """打印巡检结果"""
    dt = datetime.fromisoformat(record["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
    status_text = "正常" if record["status"] != "bad" else "异常"
    print(f"✓ 巡检完成: {dt} - {status_text} ({record['latency']}ms)")
