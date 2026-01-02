#!/usr/bin/env python3
"""GitHub DNS查询 - 从DNS服务器获取IP"""
import subprocess
import sys
import json
import re
from pathlib import Path

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

def get_ips(domain=None, dns=None):
    """从DNS服务器获取域名的IP地址"""
    domain = domain or DOMAIN
    dns = dns or DNS_SERVERS[0]
    try:
        result = subprocess.run(
            ["nslookup", domain, dns],
            capture_output=True,
            text=True,
            timeout=5
        )

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
            return all_ips

        return []
    except Exception as e:
        print(f"获取IP时出错: {e}")
        return []

def resolve_all():
    """获取所有DNS服务器和所有域名的IP并返回列表"""
    all_ips = set()
    for domain in DOMAINS:
        for dns in DNS_SERVERS:
            ips = get_ips(domain, dns)
            all_ips.update(ips)
    return sorted(all_ips)

def main():
    ips = resolve_all()
    for ip in ips:
        print(ip)
    return ips

if __name__ == "__main__":
    main()
