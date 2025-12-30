#!/usr/bin/env python3
"""GitHub工具合集 - 通用工具模块"""
import sys
import json
import importlib.util
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


def run_tool(tool_config):
    """运行工具"""
    module_path = ROOT_DIR / tool_config["module"]
    module = load_module(str(module_path))
    func = getattr(module, tool_config["function"])
    if "params" in tool_config:
        return func(**tool_config["params"])
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
