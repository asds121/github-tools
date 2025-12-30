#!/usr/bin/env python3
"""GitHub DNS查询 - 从DNS服务器获取IP"""
import subprocess
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from github_utils import load_sub_config

CONFIG = load_sub_config("GitHub-searcher-dns-DNS")

DNS_SERVERS = CONFIG["dns_servers"]
DOMAIN = CONFIG["domain"]

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
    """获取所有DNS服务器的IP并返回列表"""
    all_ips = set()
    for dns in DNS_SERVERS:
        all_ips.update(get_ips(DOMAIN, dns))
    return sorted(all_ips)

def main():
    ips = resolve_all()
    for ip in ips:
        print(ip)
    return ips

if __name__ == "__main__":
    main()
