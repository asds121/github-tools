import os

def check_file_lines():
    trace_dir = "trace"
    print("=== trace层文件行数检查 ===")
    for file in os.listdir(trace_dir):
        if file.endswith(".py"):
            file_path = os.path.join(trace_dir, file)
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = len(f.readlines())
            print(f"{file}: {lines} lines")

if __name__ == "__main__":
    check_file_lines()
