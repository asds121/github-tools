#!/usr/bin/env python3
"""定时巡检 - 定时检测 GitHub 连接状态，记录历史趋势，异常时发出告警"""
import sys
import time
import json
import threading
from pathlib import Path
from datetime import datetime, timedelta

# 导入辅助模块
import sys
from pathlib import Path

# 从通用工具包导入辅助模块
from github_utils import load_config, save_config, load_history, save_history
from github_utils.common_utils import load_module

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "trace" / "data"
DATA_DIR.mkdir(exist_ok=True)
HISTORY_DB = DATA_DIR / "inspection_history.json"
CONFIG_DB = DATA_DIR / "inspection_config.json"

# 加载依赖模块
checker_module = load_module(
    ROOT_DIR / "github-checker-检测状态" / "github_checker.py"
)
check_github = checker_module.check

class ScheduledInspector:
    """定时巡检类"""
    def __init__(self):
        self.is_running = False
        self.interval = 10 * 60  # 默认 10 分钟
        self.alert_method = "console"  # 默认控制台告警
        self.retention_days = 30  # 默认保留 30 天数据
        self.history = self.load_history()
        self.config = self.load_config()
        self.thread = None
    
    def load_config(self):
        """加载配置"""
        config = load_config(CONFIG_DB)
        if not config:
            # 默认配置
            config = {
                "interval": self.interval,
                "alert_method": self.alert_method,
                "retention_days": self.retention_days
            }
        return config
    
    def save_config(self):
        """保存配置"""
        config = {
            "interval": self.interval,
            "alert_method": self.alert_method,
            "retention_days": self.retention_days
        }
        save_config(config, CONFIG_DB)
    
    def load_history(self):
        """加载历史记录"""
        return load_history(HISTORY_DB)
    
    def save_history(self):
        """保存历史记录"""
        save_history(self.history, HISTORY_DB)
    
    def clean_old_data(self):
        """清理旧数据"""
        self.history = clean_old_data(self.history, self.retention_days)
    
    def run_inspection(self):
        """执行一次巡检"""
        try:
            result = check_github()
            timestamp = datetime.now().isoformat()
            
            inspection_record = {
                "timestamp": timestamp,
                "status": result["status"],
                "latency": result.get("ms", 0),
                "message": result.get("message", "")
            }
            
            self.history.append(inspection_record)
            self.clean_old_data()
            self.save_history()
            
            # 检查是否需要告警
            if result["status"] == "bad":
                self.alert(f"GitHub 连接异常: {result.get('message', '连接失败')}")
            
            return inspection_record
        except Exception as e:
            print(f"巡检执行失败: {e}")
            return None
    
    def alert(self, message):
        """发出告警"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        alert_message = f"[{timestamp}] 告警: {message}"
        
        if self.alert_method == "console":
            print(alert_message)
        # 可以扩展其他告警方式，如系统通知、邮件等
    
    def inspection_loop(self):
        """巡检循环"""
        while self.is_running:
            self.run_inspection()
            time.sleep(self.interval)
    
    def start(self):
        """启动巡检"""
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self.inspection_loop, daemon=True)
            self.thread.start()
            return True
        return False
    
    def stop(self):
        """停止巡检"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        return True
    
    def set_interval(self, minutes):
        """设置巡检间隔"""
        self.interval = minutes * 60
        self.save_config()
    
    def set_alert_method(self, method):
        """设置告警方式"""
        self.alert_method = method
        self.save_config()
    
    def get_today_stats(self):
        """获取今日统计数据"""
        return calculate_today_stats(self.history)
    
    def get_recent_abnormal(self, limit=5):
        """获取最近的异常记录"""
        return get_recent_abnormal(self.history, limit)
    
    def get_status(self):
        """获取当前巡检状态"""
        return {
            "is_running": self.is_running,
            "interval": self.interval,
            "alert_method": self.alert_method,
            "retention_days": self.retention_days,
            "next_inspection": datetime.now() + timedelta(seconds=self.interval) if self.is_running else None,
            "today_stats": self.get_today_stats(),
            "recent_abnormal": self.get_recent_abnormal()
        }

# 导入辅助模块
from scheduled_inspection_cli import print_status, print_inspection_result
from scheduled_inspection_stats import calculate_today_stats, get_recent_abnormal, clean_old_data

# 创建全局巡检实例
inspector = ScheduledInspector()

def run():
    """运行定时巡检功能"""
    status = inspector.get_status()
    print_status(status)
    
    return {
        "success": True,
        "status": status
    }

def start():
    """启动巡检"""
    if inspector.start():
        print("✓ 巡检服务已启动")
        return {"success": True, "message": "巡检服务已启动"}
    else:
        print("✗ 巡检服务已在运行中")
        return {"success": False, "message": "巡检服务已在运行中"}

def stop():
    """停止巡检"""
    if inspector.stop():
        print("✓ 巡检服务已停止")
        return {"success": True, "message": "巡检服务已停止"}
    else:
        print("✗ 巡检服务未在运行中")
        return {"success": False, "message": "巡检服务未在运行中"}

def set_interval(minutes):
    """设置巡检周期"""
    inspector.set_interval(minutes)
    print(f"✓ 巡检周期已设置为每 {minutes} 分钟")
    return {"success": True, "message": f"巡检周期已设置为每 {minutes} 分钟"}

def run_once():
    """立即执行一次巡检"""
    print("\n正在执行一次巡检...")
    record = inspector.run_inspection()
    if record:
        print_inspection_result(record)
        return {"success": True, "record": record}
    else:
        print("✗ 巡检执行失败")
        return {"success": False, "message": "巡检执行失败"}

def get_history():
    """获取历史记录"""
    return {
        "success": True,
        "history": inspector.history,
        "count": len(inspector.history)
    }

if __name__ == "__main__":
    run()
