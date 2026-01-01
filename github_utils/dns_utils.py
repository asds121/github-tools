#!/usr/bin/env python3
"""GitHub工具合集 - DNS查询公共功能模块"""

import socket
import time
from typing import List, Dict, Any


def resolve_dns(domain: str, dns_servers: List[str] = None, timeout: float = 5.0) -> List[str]:
    """Resolve DNS for a domain using specified DNS servers
    
    Args:
        domain: Domain name to resolve
        dns_servers: List of DNS servers to use
        timeout: Timeout for each DNS query
        
    Returns:
        List of IP addresses
    """
    if dns_servers is None:
        dns_servers = ["8.8.8.8", "223.5.5.5"]
    
    ips = []
    
    for dns_server in dns_servers:
        try:
            resolver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            resolver.settimeout(timeout)
            
            # DNS query setup
            query_id = 0x1234
            query = build_dns_query(domain)
            
            # Send query
            resolver.sendto(query, (dns_server, 53))
            response, _ = resolver.recvfrom(512)
            
            # Parse response
            response_ips = parse_dns_response(response)
            ips.extend(response_ips)
            
            resolver.close()
            
            # Stop after first successful response
            if response_ips:
                break
        except (socket.timeout, socket.error) as e:
            continue
    
    return list(set(ips))


def build_dns_query(domain: str) -> bytes:
    """Build a simple DNS query for A records"""
    # DNS header
    header = b"\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00"
    
    # DNS question (A record)
    question = b""
    for part in domain.split("."):
        question += bytes([len(part)]) + part.encode()
    question += b"\x00\x00\x01\x00\x01"
    
    return header + question


def parse_dns_response(response: bytes) -> List[str]:
    """Parse DNS response for A records"""
    ips = []
    
    # Skip header (12 bytes)
    offset = 12
    
    # Get question count
    qdcount = int.from_bytes(response[4:6], "big")
    
    # Skip questions
    for _ in range(qdcount):
        # Skip domain name
        while response[offset] != 0:
            if (response[offset] & 0xC0) == 0xC0:  # Pointer
                offset += 2
                break
            else:  # Label
                offset += response[offset] + 1
        offset += 1  # Null terminator
        offset += 4  # Type and Class
    
    # Get answer count
    ancount = int.from_bytes(response[6:8], "big")
    
    # Parse answers
    for _ in range(ancount):
        # Skip name
        if (response[offset] & 0xC0) == 0xC0:  # Pointer
            offset += 2
        else:  # Label
            while response[offset] != 0:
                offset += response[offset] + 1
            offset += 1  # Null terminator
        
        # Get type, class, ttl, data length
        rtype = int.from_bytes(response[offset:offset+2], "big")
        offset += 8  # Type, Class, TTL
        rdlength = int.from_bytes(response[offset:offset+2], "big")
        offset += 2
        
        # Parse A record
        if rtype == 1:  # A record
            ip = socket.inet_ntoa(response[offset:offset+rdlength])
            ips.append(ip)
        
        offset += rdlength
    
    return ips


def get_known_good_ips() -> Dict[str, List[str]]:
    """Get known good IPs for GitHub services
    
    Returns:
        Dict of service names to list of IPs
    """
    return {
        "github.com": [
            "140.82.113.3",
            "140.82.114.3",
            "140.82.112.3"
        ],
        "api.github.com": [
            "140.82.113.4",
            "140.82.114.4",
            "140.82.112.4"
        ],
        "assets-cdn.github.com": [
            "185.199.108.153",
            "185.199.109.153",
            "185.199.110.153",
            "185.199.111.153"
        ]
    }


def fallback_dns_lookup(domain: str) -> List[str]:
    """Fallback DNS lookup using system resolver
    
    Args:
        domain: Domain name to resolve
        
    Returns:
        List of IP addresses
    """
    try:
        return socket.gethostbyname_ex(domain)[2]
    except socket.gaierror:
        return []
