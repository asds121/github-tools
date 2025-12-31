import os

def check_subproject_lines():
    print("=== 子项目层文件行数检查 ===")
    # 获取所有子项目文件夹
    subprojects = [
        "github-checker-检测状态",
        "GitHub-guardian-守护进程",
        "GitHub-hosts-viewer-查看",
        "GitHub-repair-fix-修复",
        "GitHub-searcher-dns-DNS",
        "GitHub-searcher-test-测速"
    ]
    
    for subproject in subprojects:
        print(f"\n=== {subproject} ===")
        subproject_path = os.path.join(os.getcwd(), subproject)
        # 获取子项目中的所有.py文件
        for file in os.listdir(subproject_path):
            if file.endswith(".py"):
                file_path = os.path.join(subproject_path, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = len(f.readlines())
                print(f"{file}: {lines} lines")

if __name__ == "__main__":
    check_subproject_lines()
