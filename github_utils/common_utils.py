#!/usr/bin/env python3
"""GitHub工具合集 - 通用工具模块"""

import sys
import json
import importlib.util
import inspect
import time
import traceback
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT_DIR / "config.json"
LOG_DIR = ROOT_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

sys.path.insert(0, str(ROOT_DIR))

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CONFIG = json.load(f)


class LogLevel:
    """日志级别常量"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Logger:
    """统一日志记录和监控类"""
    
    @staticmethod
    def _write_log(level: str, message: str, details: dict = None, exception: Exception = None):
        """写入日志到文件
        
        Args:
            level: 日志级别
            message: 日志消息
            details: 详细信息（可选）
            exception: 异常对象（可选）
        """
        # 根据日志级别选择日志文件
        if level in [LogLevel.ERROR, LogLevel.CRITICAL]:
            log_file = LOG_DIR / f"error_{time.strftime('%Y-%m-%d')}.log"
        else:
            log_file = LOG_DIR / f"info_{time.strftime('%Y-%m-%d')}.log"
        
        # 构建日志条目
        log_entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "level": level,
            "message": message,
            "details": details or {}
        }
        
        # 添加异常信息
        if exception:
            log_entry["exception"] = {
                "type": type(exception).__name__,
                "message": str(exception),
                "traceback": traceback.format_exc()
            }
        
        # 写入日志文件
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            # 如果日志写入失败，打印到控制台
            print(f"Failed to write log: {e}")
    
    @staticmethod
    def debug(message: str, details: dict = None):
        """记录调试日志"""
        Logger._write_log(LogLevel.DEBUG, message, details)
    
    @staticmethod
    def info(message: str, details: dict = None):
        """记录信息日志"""
        Logger._write_log(LogLevel.INFO, message, details)
    
    @staticmethod
    def warning(message: str, details: dict = None):
        """记录警告日志"""
        Logger._write_log(LogLevel.WARNING, message, details)
    
    @staticmethod
    def error(error_type: str, message: str, exception: Exception = None, details: dict = None):
        """记录错误日志"""
        Logger._write_log(LogLevel.ERROR, message, details, exception)
    
    @staticmethod
    def critical(error_type: str, message: str, exception: Exception = None, details: dict = None):
        """记录严重错误日志"""
        Logger._write_log(LogLevel.CRITICAL, message, details, exception)
    
    @staticmethod
    def handle_exception(error_type: str, message: str, exception: Exception, details: dict = None):
        """处理异常，记录日志并返回友好的错误信息
        
        Args:
            error_type: 错误类型
            message: 错误消息
            exception: 异常对象
            details: 详细信息（可选）
        
        Returns:
            dict: 友好的错误响应
        """
        # 记录错误日志
        Logger.error(error_type, message, exception, details)
        
        # 返回友好的错误响应
        return {
            "success": False,
            "error_type": error_type,
            "message": message,
            "details": {
                "exception_type": type(exception).__name__,
                "exception_message": str(exception),
                **(details or {})
            }
        }
    
    @staticmethod
    def format_user_message(success: bool, message: str, details: dict = None, warning: str = None):
        """格式化用户友好的消息
        
        Args:
            success: 操作是否成功
            message: 主要消息
            details: 详细信息（可选）
            warning: 警告信息（可选）
        
        Returns:
            dict: 格式化的消息响应
        """
        response = {
            "success": success,
            "message": message
        }
        
        if details:
            response["details"] = details
        
        if warning:
            response["warning"] = warning
        
        return response
    
    @staticmethod
    def log_performance(operation: str, duration: float, details: dict = None):
        """记录性能日志
        
        Args:
            operation: 操作名称
            duration: 耗时（秒）
            details: 详细信息（可选）
        """
        log_file = LOG_DIR / f"performance_{time.strftime('%Y-%m-%d')}.log"
        
        log_entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "operation": operation,
            "duration_ms": round(duration * 1000),
            "details": details or {}
        }
        
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"Failed to write performance log: {e}")


class Monitor:
    """性能监控上下文管理器"""
    
    def __init__(self, operation: str, log_level: str = LogLevel.INFO, details: dict = None):
        self.operation = operation
        self.log_level = log_level
        self.details = details or {}
        self.start_time = 0
        self.end_time = 0
    
    def __enter__(self):
        self.start_time = time.time()
        Logger.info(f"开始操作: {self.operation}", self.details)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        
        # 记录性能日志
        Logger.log_performance(self.operation, duration, self.details)
        
        if exc_type is None:
            # 操作成功完成
            Logger.info(f"操作完成: {self.operation} (耗时: {duration:.3f}秒)", {
                **self.details,
                "duration": duration
            })
        else:
            # 操作失败
            Logger.error(
                "operation_failed",
                f"操作失败: {self.operation} (耗时: {duration:.3f}秒)",
                exc_val,
                {
                    **self.details,
                    "duration": duration
                }
            )


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
    """运行工具，带统一的错误处理和性能监控
    
    Args:
        tool_config: 工具配置
        output_func: 输出函数（可选，用于UI进度显示）
    
    Returns:
        dict: 工具执行结果，包含success字段
    """
    tool_name = tool_config.get('name', '未知工具')
    
    with Monitor(f"运行工具: {tool_name}", details={"tool_config": tool_config}):
        try:
            module_path = ROOT_DIR / tool_config["module"]
            module = load_module(str(module_path))
            func = getattr(module, tool_config["function"])
            
            func_params = tool_config.get("params", {}).copy()
            
            if output_func is not None:
                sig = inspect.signature(func)
                if 'output_func' in sig.parameters:
                    func_params["output_func"] = output_func
            
            # 执行工具函数
            result = func(**func_params) if func_params else func()
            
            # 确保结果包含success字段
            if isinstance(result, dict) and "success" not in result:
                result["success"] = True
            
            # 记录成功日志
            Logger.info(f"工具执行成功: {tool_name}", {
                "result": result,
                "tool_config": tool_config
            })
            
            return result
        except ModuleNotFoundError as e:
            return Logger.handle_exception(
                "module_error",
                f"无法找到工具模块: {tool_config.get('module', '未知')}",
                e,
                {"tool_config": tool_config}
            )
        except AttributeError as e:
            return Logger.handle_exception(
                "function_error",
                f"无法找到工具函数: {tool_config.get('function', '未知')}",
                e,
                {"tool_config": tool_config}
            )
        except PermissionError as e:
            return Logger.handle_exception(
                "permission_error",
                "权限不足，请以管理员身份运行程序",
                e,
                {"tool_config": tool_config}
            )
        except Exception as e:
            return Logger.handle_exception(
                "execution_error",
                f"工具执行失败: {tool_name}",
                e,
                {"tool_config": tool_config}
            )


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
