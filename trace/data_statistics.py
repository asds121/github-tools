#!/usr/bin/env python3
"""数据统计 - 收集和展示 GitHub 连接的历史统计数据和趋势分析"""
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

# 导入辅助模块
import sys
from pathlib import Path

# 添加service层到Python路径
service_path = Path(__file__).resolve().parent.parent / "service"
sys.path.insert(0, str(service_path))

from data_statistics_utils import (
    load_inspection_history,
    load_ip_quality_db,
    save_inspection_history,
    save_ip_quality_db,
    get_records_by_date_range,
    group_records_by_period
)
from data_statistics_analysis import (
    calculate_daily_stats,
    calculate_trend_stats,
    calculate_hourly_stats,
    calculate_weekly_stats,
    analyze_latency_distribution,
    get_top_abnormal_ips
)
from data_statistics_specific import (
    get_today_stats as get_today_stats_impl,
    get_weekly_stats as get_weekly_stats_impl,
    get_monthly_stats as get_monthly_stats_impl,
    get_ip_usage_distribution as get_ip_usage_distribution_impl
)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "trace" / "data"
DATA_DIR.mkdir(exist_ok=True)

# 数据文件路径
INSPECTION_HISTORY = DATA_DIR / "inspection_history.json"
IP_QUALITY_DB = ROOT_DIR / "trace" / "ip_quality_db.json"

class DataStatistics:
    """数据统计类"""
    def __init__(self):
        self.inspection_history = load_inspection_history(INSPECTION_HISTORY)
        self.ip_quality_db = load_ip_quality_db(IP_QUALITY_DB)
    
    def get_today_stats(self):
        """获取今日统计数据"""
        return get_today_stats_impl(self.inspection_history)
    
    def get_weekly_stats(self):
        """获取本周统计数据"""
        return get_weekly_stats_impl(self.inspection_history)
    
    def get_monthly_stats(self):
        """获取本月统计数据"""
        return get_monthly_stats_impl(self.inspection_history)
    
    def get_ip_usage_distribution(self):
        """获取 IP 使用分布"""
        return get_ip_usage_distribution_impl(self.ip_quality_db)
    
    def export_data(self, format="json"):
        """导出数据"""
        stats = {
            "today": self.get_today_stats(),
            "weekly": self.get_weekly_stats(),
            "monthly": self.get_monthly_stats(),
            "ip_usage": self.get_ip_usage_distribution(),
            "export_time": datetime.now().isoformat()
        }
        
        if format == "json":
            return json.dumps(stats, ensure_ascii=False, indent=2)
        elif format == "csv":
            # 生成 CSV 格式
            csv_lines = ["指标,值"]
            # 添加今日统计
            csv_lines.append(f"今日测试次数,{stats['today']['test_count']}")
            csv_lines.append(f"今日成功率(%),{stats['today']['success_rate']}")
            csv_lines.append(f"今日平均延迟(ms),{stats['today']['avg_latency']}")
            csv_lines.append(f"今日最佳延迟(ms),{stats['today']['best_latency']}")
            csv_lines.append(f"今日最差延迟(ms),{stats['today']['worst_latency']}")
            # 添加周统计
            csv_lines.append(f"本周可用率(%),{stats['weekly']['available_rate']}")
            csv_lines.append(f"本周平均延迟(ms),{stats['weekly']['avg_latency']}")
            csv_lines.append(f"本周最佳时段,{stats['weekly']['best_time_period']}")
            csv_lines.append(f"本周最差时段,{stats['weekly']['worst_time_period']}")
            # 添加月统计
            csv_lines.append(f"本月可用率(%),{stats['monthly']['available_rate']}")
            csv_lines.append(f"本月平均延迟(ms),{stats['monthly']['avg_latency']}")
            csv_lines.append(f"本月异常天数,{stats['monthly']['abnormal_days']}")
            return "\n".join(csv_lines)
        return None
    
    def print_statistics(self):
        """打印统计数据"""
        print("=" * 60)
        print("GitHub 连接统计")
        print("=" * 60)
        
        # 今日统计
        today_stats = self.get_today_stats()
        print("\n【今日统计】")
        print("-" * 50)
        print(f"检测次数:     {today_stats['test_count']}")
        print(f"成功率:       {today_stats['success_rate']}%")
        print(f"平均延迟:     {today_stats['avg_latency']}ms")
        print(f"最佳延迟:     {today_stats['best_latency']}ms")
        print(f"最差延迟:     {today_stats['worst_latency']}ms")
        if today_stats['best_ip']:
            print(f"最优 IP:      {today_stats['best_ip']}")
        
        # 本周统计
        weekly_stats = self.get_weekly_stats()
        print("\n【本周统计】")
        print("-" * 50)
        print(f"可用率:       {weekly_stats['available_rate']}%")
        print(f"平均延迟:     {weekly_stats['avg_latency']}ms")
        if weekly_stats['best_time_period']:
            print(f"最佳时段:     {weekly_stats['best_time_period']}")
        if weekly_stats['worst_time_period']:
            print(f"最差时段:     {weekly_stats['worst_time_period']}")
        
        # 本月统计
        monthly_stats = self.get_monthly_stats()
        print("\n【本月统计】")
        print("-" * 50)
        print(f"可用率:       {monthly_stats['available_rate']}%")
        print(f"平均延迟:     {monthly_stats['avg_latency']}ms")
        print(f"异常天数:     {monthly_stats['abnormal_days']} 天")
        
        # IP 使用排行榜
        ip_usage = self.get_ip_usage_distribution()
        print("\n【IP 使用排行榜】")
        print("-" * 50)
        if ip_usage:
            for i, item in enumerate(ip_usage, 1):
                print(f"{i}. {item['ip']:<18} {item['usage_count']:>6} 次  {item['success_rate']:>5}% 成功率")
        else:
            print("  暂无数据")
        
        print("\n" + "=" * 60)
        print("统计完成")
        print("=" * 60)
    
    def run(self):
        """运行数据统计功能"""
        self.print_statistics()
        
        # 返回统计结果
        return {
            "success": True,
            "today": self.get_today_stats(),
            "weekly": self.get_weekly_stats(),
            "monthly": self.get_monthly_stats(),
            "ip_usage": self.get_ip_usage_distribution()
        }

def run():
    """运行数据统计功能"""
    stats = DataStatistics()
    return stats.run()

if __name__ == "__main__":
    run()
