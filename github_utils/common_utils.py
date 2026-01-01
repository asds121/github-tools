#!/usr/bin/env python3
"""GitHub工具合集 - 通用工具模块"""
import sys
import json
import importlib.util
import inspect
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT_DIR / "config.json"

sys.path.insert(0, str(ROOT_DIR))

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CONFIG = json.load(f)


def load_sub_config(sub_dir, sub_config_name="config.json"):
    """加载子项目配置（支持根目录覆盖）
    
    子项目默认使用自己的 config.json，根目录可通过 subprojects.{子目录名} 进行覆盖
    
    Args:
        sub_dir: 子项目目录名
        sub_config_name: 子项目配置文件名
        
    Returns:
        dict: 合并后的配置
    """
    sub_path = ROOT_DIR / sub_dir / sub_config_name
    
    if sub_path.exists():
        with open(sub_path, "r", encoding="utf-8") as f:
            sub_config = json.load(f)
    else:
        sub_config = {}
    
    root_override_key = f"subprojects.{sub_dir}"
    if root_override_key in CONFIG:
        root_override = CONFIG[root_override_key]
        sub_config = _deep_merge(sub_config, root_override)
    
    return sub_config


def _deep_merge(base, override):
    """深度合并配置"""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_module(module_name, module_path=None):
    """动态加载模块
    
    Args:
        module_name: 模块名称
        module_path: 模块文件路径（可选，为兼容旧接口）
    """
    if module_path is None:
        path = Path(module_name)
    elif isinstance(module_path, (str, Path)):
        path = Path(module_path)
    else:
        path = Path(module_name)
    
    spec = importlib.util.spec_from_file_location("tool_module", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_tool(tool_config, output_func=None):
    """运行工具
    
    Args:
        tool_config: 工具配置
        output_func: 输出函数（可选，用于UI进度显示）
    """
    module_path = ROOT_DIR / tool_config["module"]
    module = load_module(str(module_path))
    func = getattr(module, tool_config["function"])
    
    func_params = tool_config.get("params", {}).copy()
    
    if output_func is not None:
        sig = inspect.signature(func)
        if 'output_func' in sig.parameters:
            func_params["output_func"] = output_func
    
    if func_params:
        return func(**func_params)
    return func()


def get_tool_config(key):
    """获取工具配置"""
    for tool in CONFIG["tools"]:
        if tool["key"] == key:
            return tool
    return None


def get_tools_order():
    """获取工具排序列表"""
    return [tool["key"] for tool in CONFIG["tools"]]


def get_ui_config():
    """获取UI配置"""
    return CONFIG["ui"]


def create_spinner():
    """创建一个简单的spinner动画控制对象"""
    import threading
    import time
    spinner_chars = "|/-\\"
    spinner_index = 0
    stop_spinner = False
    
    def spinner_thread_func(message_format, **kwargs):
        """Spinner线程函数"""
        nonlocal spinner_index
        while not stop_spinner:
            char = spinner_chars[spinner_index % len(spinner_chars)]
            message = message_format.format(char=char, **kwargs)
            print(f"\r{message}", end="", flush=True)
            spinner_index += 1
            time.sleep(0.1)
    
    def start(message_format, **kwargs):
        """启动spinner动画"""
        thread = threading.Thread(target=spinner_thread_func, args=(message_format,), kwargs=kwargs)
        thread.daemon = True
        thread.start()
        return thread
    
    def stop(thread):
        """停止spinner动画"""
        nonlocal stop_spinner
        stop_spinner = True
        thread.join()
        print("\r", end="", flush=True)  # Clear spinner line
    
    return {
        "start": start,
        "stop": stop
    }
