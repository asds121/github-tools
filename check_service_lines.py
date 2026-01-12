import os
import sys
from pathlib import Path

# 定义service层文件的最大行数限制
MAX_LINES = 400

def check_file_lines(file_path):
    """检查单个文件的行数是否符合要求"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = len(f.readlines())
        return lines <= MAX_LINES, lines
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False, 0

def check_service_lines():
    """检查service层所有Python文件的行数"""
    service_dir = Path("service")
    print(f"=== service层文件行数检查 (最大限制: {MAX_LINES}行) ===")
    
    # 检查是否存在service目录
    if not service_dir.exists():
        print(f"Error: service目录不存在")
        return 1
    
    failed_files = []
    all_files = []
    
    # 遍历service目录下的所有.py文件
    for file_path in service_dir.glob("*.py"):
        if file_path.is_file() and file_path.suffix == ".py":
            file_name = file_path.name
            is_valid, lines = check_file_lines(file_path)
            all_files.append((file_name, lines, is_valid))
            
            # 输出检查结果
            status = "✅" if is_valid else "❌"
            print(f"{status} {file_name}: {lines} lines {'(超出限制)' if not is_valid else ''}")
            
            # 记录超出限制的文件
            if not is_valid:
                failed_files.append((file_name, lines))
    
    print("=" * 50)
    
    # 输出统计结果
    total_files = len(all_files)
    passed_files = total_files - len(failed_files)
    print(f"统计结果: {passed_files}/{total_files} 文件符合要求")
    
    # 如果有文件超出限制，返回错误码
    if failed_files:
        print("\n超出限制的文件:")
        for file_name, lines in failed_files:
            print(f"  - {file_name}: {lines} 行 (超出 {lines - MAX_LINES} 行)")
        print(f"\n错误: 有 {len(failed_files)} 个文件超出了 {MAX_LINES} 行的限制")
        return 1
    else:
        print("\n所有文件都符合行数限制，通过检查!")
        return 0

def main():
    """主函数"""
    exit_code = check_service_lines()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
