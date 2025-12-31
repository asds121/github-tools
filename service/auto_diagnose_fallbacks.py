#!/usr/bin/env python3
"""一键检测修复 - 备用方案函数（Service层）"""
from pathlib import Path

# 引入trace层模块，符合service层必须引用trace层内容的要求
from trace import connection_diagnostic

ROOT_DIR = Path(__file__).resolve().parent.parent

# Service层作为Trace层的封装，调用Trace层的功能
def get_known_good_ips():
    """获取已知的可用IP列表（配置中的备用IP）"""
    return connection_diagnostic.get_known_good_ips()

def fallback_dns_lookup():
    """备用方案1: 尝试更多DNS服务器"""
    return connection_diagnostic.fallback_dns_lookup()

def fallback_known_ips():
    """备用方案2: 使用已知的可用IP"""
    return connection_diagnostic.fallback_known_ips()

def fallback_ip_quality_db():
    """备用方案3: 使用IP质量数据库中的成功IP"""
    return connection_diagnostic.fallback_ip_quality_db()

def test_single_ip(ip, port=443, timeout=2):
    """快速测试单个IP"""
    return connection_diagnostic.test_single_ip(ip, port, timeout)

def fallback_quick_test(ips):
    """备用方案4: 快速测试IP"""
    return connection_diagnostic.fallback_quick_test(ips)

def fallback_manual_config():
    """备用方案5: 提供手动配置建议"""
    return connection_diagnostic.fallback_manual_config()
