#!/usr/bin/env python3
"""GitHub工具合集 - Hosts管理公共功能模块"""

import os
import re
import time
import shutil
from typing import List, Dict, Tuple, Optional


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


def write_hosts_file(lines: List[str], hosts_path: str = None, backup: bool = True) -> Dict[str, any]:
    """Write to the hosts file with enhanced backup and validation
    
    Args:
        lines: List of lines to write to the hosts file
        hosts_path: Path to the hosts file, defaults to system hosts file
        backup: Whether to create a backup of the hosts file
    
    Returns:
        Dictionary with backup information and validation results
    """
    if hosts_path is None:
        hosts_path = get_hosts_path()
    
    hosts_path = hosts_path or get_hosts_path()
    
    # Create structured backup with timestamp and versioning
    backup_info = {
        "success": False,
        "backup_path": None,
        "timestamp": None,
    }
    
    # Create multiple backups with timestamps for better management
    backup_info = {
        "success": False,
        "error": "Backup not requested"
    }
    
    if backup:
        # Generate backup filename with timestamp
        backup_filename = f"hosts_{int(time.time())}.bak"
        backup_dir = os.path.join(os.path.dirname(hosts_path), "hosts_backups")
        
        # Create backup directory if it doesn't exist
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create backup with timestamp
        backup_path = os.path.join(backup_dir, backup_filename)
        try:
            # Read current hosts file content for backup
            current_content = read_hosts_file(hosts_path)
            
            # Write backup file
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.writelines(current_content)
            
            # Keep only the last 5 backups to save space
            cleanup_old_backups(backup_dir, max_backups=5)
            
            backup_info = {
                "success": True,
                "backup_path": backup_path,
                "timestamp": int(time.time())
            }
        except Exception as e:
            backup_info = {
                "success": False,
                "error": str(e)
            }
    
    # Write new hosts file
    try:
        with open(hosts_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        # Validate the write operation
        validation_result = validate_hosts_write(hosts_path, lines)
        
        return {
            "backup": backup_info,
            "validation": validation_result,
            "write_time": int(time.time())
        }
    except PermissionError:
        raise PermissionError(f"Permission denied when writing hosts file: {hosts_path}")
    except Exception as e:
        raise Exception(f"Error writing hosts file: {str(e)}")


def cleanup_old_backups(backup_dir: str, max_backups: int = 5) -> List[str]:
    """Clean up old backups, keep only the most recent max_backups
    
    Args:
        backup_dir: Path to backup directory
        max_backups: Maximum number of backups to keep
    
    Returns: List of removed backup files
    """
    if not os.path.exists(backup_dir):
        return []
    
    # Get all backup files, sorted by modification time (newest first)
    backup_files = []
    for filename in os.listdir(backup_dir):
        if filename.startswith("hosts_") and filename.endswith(".bak"):
            filepath = os.path.join(backup_dir, filename)
            mtime = os.path.getmtime(filepath)
            backup_files.append((mtime, filepath, filename))
    
    # Sort by modification time (newest first)
    backup_files.sort(reverse=True, key=lambda x: x[0])
    
    # Keep only the most recent max_backups
    kept_backups = backup_files[:max_backups]
    removed_files = []
    
    # Remove old backups
    for _, filepath, filename in backup_files[max_backups:]:
        try:
            os.remove(filepath)
            removed_files.append(filename)
        except Exception as e:
            print(f"Failed to remove old backup {filename}: {e}")
    
    return removed_files


def validate_hosts_write(hosts_path: str, original_lines: List[str]) -> Dict[str, any]:
    """Validate that the hosts file was written correctly
    
    Args:
        hosts_path: Path to hosts file
        original_lines: Original lines written
    
    Returns:
        Validation results
    """
    # Read back the file to verify
    try:
        with open(hosts_path, 'r', encoding='utf-8') as f:
            written_lines = f.readlines()
        
        # Check if content matches what we wrote
        original_content = ''.join(original_lines)
        written_content = ''.join(written_lines)
        
        # Normalize both contents for comparison (remove extra newlines)
        normalized_original = original_content.strip()
        normalized_written = written_content.strip()
        
        is_match = normalized_original == normalized_written
        
        return {
            "success": is_match,
            "original_content": original_content,
            "written_content": written_content,
            "match_score": 100 if is_match else 70
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def backup_hosts_with_version(hosts_path: Optional[str] = None, backup_dir: Optional[str] = None) -> Dict[str, any]:
    """Create a versioned backup of the hosts file
    
    Args:
        hosts_path: Path to hosts file, defaults to system hosts
        backup_dir: Directory to store backups, defaults to hosts_backups subdir
    
    Returns:
        Dictionary with backup info
    """
    if hosts_path is None:
        hosts_path = get_hosts_path()
    
    backup_dir = backup_dir or os.path.join(os.path.dirname(hosts_path), "hosts_backups")
    os.makedirs(backup_dir, exist_ok=True)
    
    # Generate backup filename with timestamp
    timestamp = int(time.time())
    backup_filename = f"hosts_{timestamp}.bak"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    try:
        # Copy hosts file to backup location
        shutil.copy2(hosts_path, backup_path)
        
        # Clean up old backups, keep only last 5
        cleanup_old_backups(backup_dir, max_backups=5)
        
        return {
            "success": True,
            "backup_path": backup_path,
            "timestamp": timestamp,
            "hosts_path": hosts_path
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "hosts_path": hosts_path
        }

def cleanup_old_backups(backup_dir: str, max_backups: int = 5) -> List[str]:
    """Clean up old backups, keep only the most recent ones
    
    Args:
        backup_dir: Directory containing backup files
        max_backups: Maximum number of backups to keep
    
    Returns:
        List of removed backup filenames
    """
    if not os.path.exists(backup_dir):
        return []
    
    # Get all backup files with their modification times
    backup_files = []
    for filename in os.listdir(backup_dir):
        if filename.startswith("hosts_") and filename.endswith(".bak"):
            filepath = os.path.join(backup_dir, filename)
            mtime = os.path.getmtime(filepath)
            backup_files.append((mtime, filepath, filename))
    
    # Sort by modification time (newest first)
    backup_files.sort(reverse=True, key=lambda x: x[0])
    
    # Keep only the most recent backups
    kept_backups = backup_files[:max_backups]
    removed_files = []
    
    # Remove old backups
    for _, filepath, filename in backup_files[max_backups:]:
        try:
            os.remove(filepath)
            removed_files.append(filename)
        except Exception as e:
            print(f"Failed to remove old backup {filename}: {e}")
    
    return removed_files

def restore_hosts_from_backup(backup_path: str, hosts_path: Optional[str] = None) -> Dict[str, any]:
    """Restore hosts file from a specific backup
    
    Args:
        backup_path: Path to backup file
        hosts_path: Target hosts file path, defaults to system hosts
    
    Returns:
        Dictionary with restore results
    """
    if not os.path.exists(backup_path):
        return {"success": False, "error": "Backup file not found"}
    
    if hosts_path is None:
        hosts_path = get_hosts_path()
    
    try:
        # Validate backup content
        with open(backup_path, 'r', encoding='utf-8') as f:
            backup_content = f.read()
        
        # Check if backup contains valid content
        if len(backup_content.strip()) == 0:
            return {"success": False, "error": "Backup file is empty"}
        
        # Copy backup to hosts file
        shutil.copy2(backup_path, hosts_path)
        
        # Validate the restore was successful
        validation = validate_hosts_file(hosts_path)
        
        return {
            "success": True,
            "backup_used": backup_path,
            "restored_to": hosts_path,
            "validation": validation
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def validate_hosts_file(hosts_path: str) -> Dict[str, any]:
    """Validate a hosts file is working correctly
    
    Args:
        hosts_path: Path to hosts file
    
    Returns:
        Dictionary with validation results
    """
    # Try to read the hosts file and check content
    try:
        with open(hosts_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for GitHub entries
        github_entries = re.findall(r'github\.com', content, re.IGNORECASE)
        has_github = len(github_entries) > 0
        
        return {
            "is_valid": True,
            "has_github_entries": has_github,
            "github_entry_count": len(github_entries),
            "validation_time": int(time.time())
        }
    except Exception as e:
        return {
            "is_valid": False, 
            "error": str(e),
            "validation_time": int(time.time())
        }

def get_all_backups(hosts_path: Optional[str] = None) -> List[Dict[str, any]]:
    """Get all available backups for the hosts file
    
    Args:
        hosts_path: Path to hosts file, defaults to system hosts
    
    Returns:
        List of backup info dictionaries, sorted by timestamp (newest first)
    """
    if hosts_path is None:
        hosts_path = get_hosts_path()
    
    backup_dir = os.path.join(os.path.dirname(hosts_path), "hosts_backups")
    if not os.path.exists(backup_dir):
        return []
    
    backups = []
    for filename in os.listdir(backup_dir):
        if filename.startswith("hosts_") and filename.endswith(".bak"):
            filepath = os.path.join(backup_dir, filename)
            # Extract timestamp from filename: hosts_1234567890.bak -> 1234567890
            try:
                timestamp = int(filename[6:-4])  # hosts_1234567890.bak -> 1234567890
                backups.append({
                    "filename": filename,
                    "path": filepath,
                    "timestamp": timestamp,
                    "mtime": os.path.getmtime(filepath),
                    "size": os.path.getsize(filepath)
                })
            except (ValueError, IndexError):
                continue
    
    # Sort backups by timestamp (newest first)
    backups.sort(key=lambda x: x["timestamp"], reverse=True)
    return backups


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
