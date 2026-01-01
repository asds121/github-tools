#!/usr/bin/env python3
"""GitHub工具合集 - Hosts管理公共功能模块"""

import os
import re
from typing import List, Dict, Tuple


def get_hosts_path() -> str:
    """Get the path to the hosts file based on the operating system
    
    Returns:
        Path to the hosts file
    """
    if os.name == 'nt':  # Windows
        return r'C:\Windows\System32\drivers\etc\hosts'
    else:  # Linux, macOS, etc.
        return '/etc/hosts'


def read_hosts_file(hosts_path: str = None) -> List[str]:
    """Read the hosts file
    
    Args:
        hosts_path: Path to the hosts file, defaults to system hosts file
        
    Returns:
        List of lines from the hosts file
    """
    if hosts_path is None:
        hosts_path = get_hosts_path()
    
    try:
        with open(hosts_path, 'r', encoding='utf-8') as f:
            return f.readlines()
    except PermissionError:
        raise PermissionError(f"Permission denied when reading hosts file: {hosts_path}")
    except FileNotFoundError:
        raise FileNotFoundError(f"Hosts file not found: {hosts_path}")
    except Exception as e:
        raise Exception(f"Error reading hosts file: {str(e)}")


def write_hosts_file(lines: List[str], hosts_path: str = None, backup: bool = True) -> None:
    """Write to the hosts file
    
    Args:
        lines: List of lines to write to the hosts file
        hosts_path: Path to the hosts file, defaults to system hosts file
        backup: Whether to create a backup of the hosts file
    """
    if hosts_path is None:
        hosts_path = get_hosts_path()
    
    # Create backup if requested
    if backup:
        backup_path = hosts_path + '.bak'
        try:
            existing_lines = read_hosts_file(hosts_path)
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.writelines(existing_lines)
        except Exception as e:
            # Backup failed, but continue with writing
            pass
    
    try:
        with open(hosts_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
    except PermissionError:
        raise PermissionError(f"Permission denied when writing hosts file: {hosts_path}")
    except Exception as e:
        raise Exception(f"Error writing hosts file: {str(e)}")


def find_hosts_entries(lines: List[str], domain: str = None) -> List[Dict[str, str]]:
    """Find hosts entries for a specific domain or all domains
    
    Args:
        lines: List of lines from the hosts file
        domain: Domain to search for, defaults to all domains
        
    Returns:
        List of dictionaries with host entry details
    """
    entries = []
    host_pattern = re.compile(r'^\s*(\d+\.\d+\.\d+\.\d+)\s+([^\s#]+)')
    
    for i, line in enumerate(lines):
        match = host_pattern.match(line)
        if match:
            ip = match.group(1)
            host = match.group(2)
            
            if domain is None or host == domain:
                entries.append({
                    'line_number': i + 1,
                    'ip': ip,
                    'host': host,
                    'full_line': line.rstrip()
                })
    
    return entries


def add_host_entry(lines: List[str], ip: str, host: str) -> List[str]:
    """Add a new host entry to the hosts file lines
    
    Args:
        lines: List of lines from the hosts file
        ip: IP address to add
        host: Hostname to add
        
    Returns:
        Updated list of lines with the new host entry
    """
    # Check if entry already exists
    existing_entries = find_hosts_entries(lines, host)
    if existing_entries:
        # Update existing entry
        for entry in existing_entries:
            lines[entry['line_number'] - 1] = f'{ip}\t{host}\n'
    else:
        # Add new entry
        lines.append(f'{ip}\t{host}\n')
    
    return lines


def remove_host_entry(lines: List[str], host: str) -> List[str]:
    """Remove host entries for a specific domain
    
    Args:
        lines: List of lines from the hosts file
        host: Hostname to remove
        
    Returns:
        Updated list of lines with the host entry removed
    """
    # Find all entries for the host
    existing_entries = find_hosts_entries(lines, host)
    
    # Remove entries in reverse order to avoid index shifting issues
    for entry in sorted(existing_entries, key=lambda x: x['line_number'], reverse=True):
        del lines[entry['line_number'] - 1]
    
    return lines


def update_host_entries(lines: List[str], entries: Dict[str, str]) -> List[str]:
    """Update multiple host entries
    
    Args:
        lines: List of lines from the hosts file
        entries: Dictionary of hostname to IP address
        
    Returns:
        Updated list of lines with all host entries updated
    """
    updated_lines = lines.copy()
    
    for host, ip in entries.items():
        updated_lines = add_host_entry(updated_lines, ip, host)
    
    return updated_lines


def backup_hosts_file(hosts_path: str = None, backup_path: str = None) -> str:
    """Create a backup of the hosts file
    
    Args:
        hosts_path: Path to the hosts file, defaults to system hosts file
        backup_path: Path to save the backup, defaults to hosts_path + '.bak'
        
    Returns:
        Path to the backup file
    """
    if hosts_path is None:
        hosts_path = get_hosts_path()
    
    if backup_path is None:
        backup_path = hosts_path + '.bak'
    
    lines = read_hosts_file(hosts_path)
    
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    return backup_path


def restore_hosts_file(backup_path: str, hosts_path: str = None) -> None:
    """Restore the hosts file from a backup
    
    Args:
        backup_path: Path to the backup file
        hosts_path: Path to the hosts file, defaults to system hosts file
    """
    if hosts_path is None:
        hosts_path = get_hosts_path()
    
    with open(backup_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    write_hosts_file(lines, hosts_path, backup=False)


def get_github_host_entries(lines: List[str]) -> Dict[str, str]:
    """Get all GitHub-related host entries from the hosts file
    
    Args:
        lines: List of lines from the hosts file
        
    Returns:
        Dictionary of GitHub hostnames to IP addresses
    """
    github_entries = {}
    entries = find_hosts_entries(lines)
    
    for entry in entries:
        host = entry['host']
        if 'github' in host.lower():
            github_entries[host] = entry['ip']
    
    return github_entries
