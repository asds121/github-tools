#!/usr/bin/env python3
"""一键检测修复 - 自动检测并修复GitHub连接问题（基础入口）"""
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Import from github_utils
from github_utils.common_utils import load_module

ROOT_DIR = Path(__file__).resolve().parent.parent

def run(progress_callback=None):
    """一键检测修复 - 自动检测并修复GitHub连接问题
    
    Args:
        progress_callback: 进度回调函数，接收参数：(stage, message, progress_percent)
                          stage: 当前阶段名称
                          message: 当前阶段状态消息
                          progress_percent: 整体进度百分比 (0-100)
    """
    print("=" * 60)
    print("GitHub 一键检测修复")
    print("=" * 60)
    
    # 调用service层的复杂诊断修复逻辑
    try:
        # 导入service层的自动诊断服务
        from service import auto_diagnose_service
        
        # 调用service层的run函数处理实际的诊断修复
        result = auto_diagnose_service.run(progress_callback)
        
        return result
    except Exception as e:
        print(f"\n[错误] 调用诊断修复服务失败: {e}")
        print("[建议] 检查service层auto_diagnose_service.py是否正确实现")
        return {"success": False, "action": "fail", "message": f"调用诊断服务失败: {e}"}


# 直接运行时的入口
if __name__ == "__main__":
    run()
