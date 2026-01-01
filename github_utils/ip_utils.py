#!/usr/bin/env python3
"""GitHub工具合集 - IP测试公共功能模块"""

import time
import socket
import ssl
from typing import List, Dict, Tuple


def test_ip_speed(ip: str, port: int = 443, timeout: float = 3.0) -> Dict[str, any]:
    """Test the speed of a single IP
    
    Args:
        ip: IP address to test
        port: Port to connect to
        timeout: Timeout for the connection
        
    Returns:
        Dict with speed test results
    """
    result = {
        "ip": ip,
        "port": port,
        "ok": False,
        "ms": 0,
        "error": None
    }
    
    try:
        start_time = time.time()
        
        # Create socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        # Connect to IP
        sock.connect((ip, port))
        
        # Wrap with SSL
        context = ssl.create_default_context()
        with context.wrap_socket(sock, server_hostname="github.com") as ssock:
            # Send simple HTTP request
            request = f"GET / HTTP/1.1\r\nHost: github.com\r\nConnection: close\r\n\r\n"
            ssock.sendall(request.encode())
            
            # Receive response
            response = ssock.recv(1024)
            
            # Calculate time
            end_time = time.time()
            ms = round((end_time - start_time) * 1000)
            
            result["ok"] = True
            result["ms"] = ms
            result["response_length"] = len(response)
    
    except socket.timeout:
        result["error"] = "timeout"
    except ssl.SSLError as e:
        result["error"] = f"ssl_error: {str(e)}"
    except socket.error as e:
        result["error"] = f"socket_error: {str(e)}"
    except Exception as e:
        result["error"] = f"unknown_error: {str(e)}"
    
    return result


def test_ips_speeds(ips: List[str], port: int = 443, timeout: float = 3.0, max_workers: int = 10) -> List[Dict[str, any]]:
    """Test the speed of multiple IPs in parallel
    
    Args:
        ips: List of IP addresses to test
        port: Port to connect to
        timeout: Timeout for each connection
        max_workers: Maximum number of parallel workers
        
    Returns:
        List of speed test results
    """
    results = []
    
    # Use sequential testing for simplicity and compatibility
    # In a real implementation, we could use concurrent.futures for parallel testing
    for ip in ips:
        result = test_ip_speed(ip, port, timeout)
        results.append(result)
    
    return results


def get_best_ip(ips: List[str], port: int = 443, timeout: float = 3.0) -> Tuple[str, float]:
    """Get the best IP from a list based on speed test
    
    Args:
        ips: List of IP addresses to test
        port: Port to connect to
        timeout: Timeout for each connection
        
    Returns:
        Tuple of (best_ip, best_ms), or (None, 0) if no IPs are available
    """
    results = test_ips_speeds(ips, port, timeout)
    
    # Filter out failed tests
    successful_results = [r for r in results if r["ok"]]
    
    if not successful_results:
        return None, 0
    
    # Sort by latency
    successful_results.sort(key=lambda x: x["ms"])
    
    best_result = successful_results[0]
    return best_result["ip"], best_result["ms"]


def is_ip_valid(ip: str) -> bool:
    """Check if an IP address is valid
    
    Args:
        ip: IP address to check
        
    Returns:
        True if the IP is valid, False otherwise
    """
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False


def filter_valid_ips(ips: List[str]) -> List[str]:
    """Filter valid IPs from a list
    
    Args:
        ips: List of IP addresses to filter
        
    Returns:
        List of valid IP addresses
    """
    return [ip for ip in ips if is_ip_valid(ip)]
