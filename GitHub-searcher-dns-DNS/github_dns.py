#!/usr/bin/env python3
"""GitHub DNS查询 - 从DNS服务器获取IP，带缓存功能"""
import subprocess
import sys
import json
import re
import time
from pathlib import Path
from datetime import datetime, timedelta

# DNS缓存配置
DNS_CACHE = {}
CACHE_EXPIRY = 300  # 缓存过期时间，5分钟

# DNS服务器可用性检测配置
DNS_SERVER_STATUS = {}
DNS_CHECK_EXPIRY = 600  # DNS服务器状态检查过期时间，10分钟
DNS_CHECK_TIMEOUT = 2  # DNS服务器检查超时时间，2秒

# 直接读取本地配置文件
CONFIG_PATH = Path(__file__).resolve().parent / "config.json"
if CONFIG_PATH.exists():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        CONFIG = json.load(f)
    DNS_SERVERS = CONFIG["dns_servers"]
    # 支持单域名和多域名配置
    if "domains" in CONFIG:
        DOMAINS = CONFIG["domains"]
        DOMAIN = DOMAINS[0]  # 保持向后兼容
    else:
        DOMAINS = [CONFIG["domain"]]
        DOMAIN = CONFIG["domain"]
else:
    # 默认配置
    DNS_SERVERS = ["114.114.114.114", "8.8.8.8", "1.1.1.1", "8.8.4.4", "1.0.0.1", "223.5.5.5"]
    DOMAINS = ["github.com", "api.github.com"]
    DOMAIN = "github.com"

def get_cache_key(domain, dns):
    """生成缓存键"""
    return f"{domain}:{dns}"


def is_cache_valid(cache_entry):
    """检查缓存是否有效"""
    if not cache_entry:
        return False
    expire_time = cache_entry.get("expire_time")
    if not expire_time:
        return False
    current_time = time.time()
    return current_time < expire_time


def get_cached_ips(domain, dns):
    """从缓存获取IP"""
    cache_key = get_cache_key(domain, dns)
    cache_entry = DNS_CACHE.get(cache_key)
    if is_cache_valid(cache_entry):
        return cache_entry.get("ips", [])
    return None


def update_cache(domain, dns, ips):
    """更新缓存"""
    cache_key = get_cache_key(domain, dns)
    expire_time = time.time() + CACHE_EXPIRY
    DNS_CACHE[cache_key] = {
        "ips": ips,
        "expire_time": expire_time,
        "updated_at": time.time()
    }


def get_ips(domain=None, dns=None):
    """从DNS服务器获取域名的IP地址，带缓存功能"""
    domain = domain or DOMAIN
    dns = dns or DNS_SERVERS[0]
    
    # 1. 检查缓存
    cached_ips = get_cached_ips(domain, dns)
    if cached_ips:
        print(f"[DNS缓存命中] {domain} at {dns} 缓存有效，直接返回 {len(cached_ips)} 个IP")
        return cached_ips
    
    # 2. 缓存未命中，执行DNS查询
    try:
        # 减少超时时间，增加重试机制
        for attempt in range(2):
            try:
                result = subprocess.run(
                    ["nslookup", domain, dns],
                    capture_output=True,
                    text=True,
                    timeout=3  # 减少超时时间到3秒
                )
                
                if result.returncode == 0:
                    break
            except subprocess.TimeoutExpired:
                if attempt == 1:  # 第二次尝试仍失败
                    raise
                continue
        
        output = result.stdout
        stderr = result.stderr

        has_non_authoritative = '非权威应答' in stderr or 'Non-authoritative answer' in stderr

        lines = output.split('\n')
        domain_start_index = -1
        for i, line in enumerate(lines):
            if '名称:' in line or 'Name:' in line:
                domain_start_index = i
                break

        all_ips = []
        if domain_start_index >= 0:
            after_domain_lines = '\n'.join(lines[domain_start_index:])
            all_ips = re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', after_domain_lines)

        if not all_ips and not has_non_authoritative:
            all_ips = re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', output)

        all_ips = [ip for ip in all_ips if not ip.startswith('127.')]
        all_ips = list(dict.fromkeys(all_ips))

        if all_ips:
            # 3. 更新缓存
            update_cache(domain, dns, all_ips)
            print(f"[DNS缓存更新] {domain} at {dns} 保存到缓存，{len(all_ips)}个IP")
            return all_ips

        return []
    except subprocess.TimeoutExpired:
        print(f"DNS查询超时: nslookup {domain} {dns}")
        return []
    except Exception as e:
        print(f"获取IP时出错: {e}")
        return []

def resolve_all():
    """获取所有DNS服务器和所有域名的IP并返回列表，带缓存支持和动态DNS服务器选择"""
    all_ips = set()
    cache_hits = 0
    cache_misses = 0
    
    # 获取可用的DNS服务器列表
    available_dns_servers = get_available_dns_servers()
    # 使用最优的前3个DNS服务器，减少请求次数
    optimal_dns_servers = get_optimal_dns_servers(limit=3)
    
    print(f"[DNS缓存状态] 开始解析 {len(DOMAINS)} 个域名，使用 {len(optimal_dns_servers)} 个最优DNS服务器，当前缓存条目: {len(DNS_CACHE)}")
    print(f"[DNS缓存状态] 可用DNS服务器: {available_dns_servers}, 最优DNS服务器: {optimal_dns_servers}")
    
    for domain in DOMAINS:
        for dns in optimal_dns_servers:  # 使用最优DNS服务器列表
            # 使用get_ips函数，该函数已支持缓存
            ips = get_ips(domain, dns)
            all_ips.update(ips)
            
            # 统计缓存命中情况
            cache_key = get_cache_key(domain, dns)
            cache_entry = DNS_CACHE.get(cache_key)
            if cache_entry and is_cache_valid(cache_entry):
                cache_hits += 1
            else:
                cache_misses += 1
    
    print(f"[DNS缓存统计] 缓存命中: {cache_hits}次, 缓存未命中: {cache_misses}次, 命中率: {cache_hits/(cache_hits+cache_misses)*100:.1f}%")
    print(f"[DNS缓存状态] 最终缓存条目: {len(DNS_CACHE)}, 总共获取到 {len(all_ips)} 个唯一IP")
    
    return sorted(all_ips)


def clear_cache(domain=None, dns=None):
    """清除DNS缓存"""
    if domain and dns:
        # 清除特定域名和DNS的缓存
        cache_key = get_cache_key(domain, dns)
        if cache_key in DNS_CACHE:
            del DNS_CACHE[cache_key]
            print(f"[DNS缓存清除] 已清除 {domain} at {dns} 的缓存")
    elif domain:
        # 清除特定域名的所有缓存
        keys_to_delete = [k for k in DNS_CACHE.keys() if k.startswith(f"{domain}:")]
        for key in keys_to_delete:
            del DNS_CACHE[key]
        print(f"[DNS缓存清除] 已清除 {domain} 的所有缓存，共 {len(keys_to_delete)} 条")
    else:
        # 清除所有缓存
        cache_count = len(DNS_CACHE)
        DNS_CACHE.clear()
        print(f"[DNS缓存清除] 已清除所有DNS缓存，共 {cache_count} 条")


def test_dns_server(dns_server):
    """测试DNS服务器可用性"""
    try:
        # 使用nsloopk测试DNS服务器是否可用
        result = subprocess.run(
            ["nslookup", "github.com", dns_server],
            capture_output=True,
            text=True,
            timeout=DNS_CHECK_TIMEOUT
        )
        return result.returncode == 0
    except Exception as e:
        print(f"[DNS服务器检测] 测试 {dns_server} 失败: {e}")
        return False


def update_dns_status(dns_server, status):
    """更新DNS服务器状态"""
    DNS_SERVER_STATUS[dns_server] = {
        "available": status,
        "checked_at": time.time(),
        "expire_time": time.time() + DNS_CHECK_EXPIRY
    }


def is_dns_status_valid(status_entry):
    """检查DNS服务器状态是否有效"""
    if not status_entry:
        return False
    expire_time = status_entry.get("expire_time")
    if not expire_time:
        return False
    current_time = time.time()
    return current_time < expire_time


def get_dns_server_status(dns_server):
    """获取DNS服务器状态"""
    status_entry = DNS_SERVER_STATUS.get(dns_server)
    if is_dns_status_valid(status_entry):
        return status_entry.get("available", False)
    
    # 状态过期或不存在，重新检测
    status = test_dns_server(dns_server)
    update_dns_status(dns_server, status)
    return status


def get_available_dns_servers():
    """获取可用的DNS服务器列表"""
    available_servers = []
    all_servers = DNS_SERVERS.copy()
    
    print(f"[DNS服务器检测] 开始检测 {len(all_servers)} 个DNS服务器...")
    
    # 检测所有DNS服务器状态
    for dns_server in all_servers:
        status = get_dns_server_status(dns_server)
        if status:
            available_servers.append(dns_server)
    
    if not available_servers:
        # 没有可用DNS服务器，返回默认列表
        print(f"[DNS服务器检测] 所有DNS服务器均不可用，返回默认列表")
        return all_servers
    
    print(f"[DNS服务器检测] 检测完成，可用DNS服务器: {available_servers}, 可用率: {len(available_servers)/len(all_servers)*100:.1f}%")
    return available_servers


def get_optimal_dns_servers(limit=3):
    """获取最优的DNS服务器列表（可用且响应最快）"""
    available_servers = get_available_dns_servers()
    
    if len(available_servers) <= limit:
        return available_servers
    
    # 简单实现：随机选择前limit个可用服务器
    # 更复杂的实现可以测试响应时间并排序
    print(f"[DNS服务器检测] 从 {len(available_servers)} 个可用服务器中选择前 {limit} 个")
    return available_servers[:limit]


def get_cache_stats():
    """获取缓存统计信息"""
    current_time = time.time()
    valid_entries = 0
    total_entries = len(DNS_CACHE)
    
    for entry in DNS_CACHE.values():
        if current_time < entry.get("expire_time", 0):
            valid_entries += 1
    
    return {
        "total_entries": total_entries,
        "valid_entries": valid_entries,
        "invalid_entries": total_entries - valid_entries,
        "cache_usage": valid_entries / total_entries * 100 if total_entries > 0 else 0
    }

def main():
    ips = resolve_all()
    for ip in ips:
        print(ip)
    return ips

if __name__ == "__main__":
    main()
