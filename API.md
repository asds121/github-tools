# GitHub工具合集 - API文档

## 概述

本项目提供了一系列用于优化GitHub访问的Python工具，包含连接检测、DNS查询、IP测速、Hosts修复、系统诊断和实时守护等功能。

## 模块结构

```
├── github_utils/        # 通用工具层
│   ├── __init__.py
│   ├── common_utils.py    # 通用工具函数
│   ├── async_utils.py     # 异步任务处理
│   └── gui_utils.py       # GUI构建工具
├── service/             # 业务逻辑层
│   ├── auto_diagnose_service.py        # 自动诊断服务
│   ├── auto_diagnose_fallbacks.py      # 自动诊断备用方案
│   ├── config_utils.py                 # 配置工具
│   ├── connection_diagnostic_service.py # 连接诊断服务
│   ├── fault_analysis_service.py       # 故障分析服务
│   ├── guardian_utils.py               # 守护进程工具
│   ├── ip_quality_service.py           # IP质量服务
│   └── scheduled_inspection_cli.py     # 定时检查CLI
└── trace/               # 核心功能层
    ├── fault_analysis.py          # 故障分析
    ├── connection_diagnostic.py   # 连接诊断
    ├── hosts_manager.py           # Hosts管理
    ├── ip_quality_db.py           # IP质量数据库
    └── scheduled_inspection.py    # 定时检查
```

## 1. common_utils.py

### 1.1 load_sub_config

加载子项目配置（支持根目录覆盖）

```python
def load_sub_config(sub_dir, sub_config_name="config.json"):
    """
    加载子项目配置（支持根目录覆盖）

    Args:
        sub_dir: 子项目目录名
        sub_config_name: 子项目配置文件名

    Returns:
        dict: 合并后的配置
    """
```

### 1.2 load_module

动态加载模块

```python
def load_module(module_name, module_path=None):
    """
    动态加载模块

    Args:
        module_name: 模块名称
        module_path: 模块文件路径（可选，为兼容旧接口）

    Returns:
        module: 加载的模块对象
    """
```

### 1.3 run_tool

运行工具

```python
def run_tool(tool_config, output_func=None):
    """
    运行工具

    Args:
        tool_config: 工具配置
        output_func: 输出函数（可选，用于UI进度显示）

    Returns:
        Any: 工具运行结果
    """
```

### 1.4 get_tool_config

获取工具配置

```python
def get_tool_config(key):
    """
    获取工具配置

    Args:
        key: 工具唯一标识

    Returns:
        dict: 工具配置字典
    """
```

### 1.5 get_tools_order

获取工具排序列表

```python
def get_tools_order():
    """
    获取工具排序列表

    Returns:
        list: 工具key列表，按配置顺序排列
    """
```

### 1.6 get_ui_config

获取UI配置

```python
def get_ui_config():
    """
    获取UI配置

    Returns:
        dict: UI配置字典
    """
```

## 2. async_utils.py

### 2.1 Tooltip类

工具提示组件

```python
class Tooltip:
    """
    工具提示组件

    Args:
        widget: 绑定的Tkinter组件
        text: 提示文本
        ui_config: UI配置字典
    """

    def __init__(self, widget, text, ui_config):
        pass

    def show_tooltip(self, event=None):
        """显示工具提示"""
        pass

    def hide_tooltip(self, event=None):
        """隐藏工具提示"""
        pass
```

### 2.2 AsyncTaskRunner类

异步任务运行器

```python
class AsyncTaskRunner:
    """
    异步任务运行器

    Args:
        result_callback: 结果回调函数，接收(tool_key, status, data)参数
    """

    def __init__(self, result_callback=None):
        pass

    def run_tool_async(self, tool_key, tool_config, run_tool_func, btn,
                      on_complete=None, output_func=None):
        """
        异步运行工具

        Args:
            tool_key: 工具唯一标识
            tool_config: 工具配置
            run_tool_func: 运行工具的函数
            btn: 按钮组件，用于禁用/启用
            on_complete: 完成回调
            output_func: 输出函数，用于显示进度

        Returns:
            self: 实例自身，支持链式调用
        """
        pass

    def check_queue(self, buttons, on_status_change=None):
        """
        检查任务队列

        Args:
            buttons: 按钮组件列表
            on_status_change: 状态变化回调

        Returns:
            bool: 是否还有运行中的任务
        """
        pass
```

### 2.3 ResultPanel类

结果面板组件

```python
class ResultPanel:
    """
    结果面板组件

    Args:
        parent: 父容器组件
        ui_config: UI配置字典
        layout_config: 布局配置字典
    """

    def __init__(self, parent, ui_config, layout_config):
        pass

    def insert(self, content, tag=None):
        """
        插入文本内容

        Args:
            content: 要插入的文本
            tag: 文本标签（可选）
        """
        pass

    def clear(self):
        """清空结果面板"""
        pass

    def show_json(self, data):
        """
        显示JSON数据

        Args:
            data: 要显示的JSON数据
        """
        pass

    def create_progress_output_func(self):
        """
        创建进度条输出函数

        Returns:
            function: 进度输出函数
        """
        pass

    def clear_progress(self):
        """
        清除进度条
        """
        pass
```

## 3. gui_utils.py

### 3.1 create_main_window

创建主窗口

```python
def create_main_window():
    """
    创建主窗口

    Returns:
        Tk: Tkinter主窗口对象
    """
    pass
```

### 3.2 setup_window_style

设置窗口样式

```python
def setup_window_style(root):
    """
    设置窗口样式

    Args:
        root: Tkinter主窗口对象
    """
    pass
```

### 3.3 create_notebook

创建笔记本组件

```python
def create_notebook(root, ui_config):
    """
    创建笔记本组件

    Args:
        root: 父容器
        ui_config: UI配置字典

    Returns:
        ttk.Notebook: 笔记本组件
    """
    pass
```

### 3.4 create_tab

创建标签页

```python
def create_tab(notebook, tab_text, padding):
    """
    创建标签页

    Args:
        notebook: 笔记本组件
        tab_text: 标签页文本
        padding: 内边距

    Returns:
        ttk.Frame: 标签页框架
    """
    pass
```

### 3.5 create_button_panel

创建按钮面板

```python
def create_button_panel(parent):
    """
    创建按钮面板

    Args:
        parent: 父容器

    Returns:
        ttk.Frame: 按钮面板框架
    """
    pass
```

### 3.6 create_exit_button

创建退出按钮

```python
def create_exit_button(parent, exit_func, ui_config):
    """
    创建退出按钮

    Args:
        parent: 父容器
        exit_func: 退出函数
        ui_config: UI配置字典

    Returns:
        ttk.Button: 退出按钮
    """
    pass
```

## 4. service层模块

### 4.1 auto_diagnose_service.py

自动诊断服务，提供一键检测修复GitHub连接问题的功能。

#### 4.1.1 run

一键检测修复 - 自动检测并修复GitHub连接问题

```python
def run(progress_callback=None):
    """
    一键检测修复 - 自动检测并修复GitHub连接问题

    Args:
        progress_callback: 进度回调函数，接收参数：(stage, message, progress_percent)
                          stage: 当前阶段名称
                          message: 当前阶段状态消息
                          progress_percent: 整体进度百分比 (0-100)

    Returns:
        dict: 修复结果，包含success、action、message、latency等字段
    """
    pass
```

### 4.2 auto_diagnose_fallbacks.py

自动诊断备用方案函数，提供多种备用修复策略。

#### 4.2.1 get_known_good_ips

获取已知的可用IP列表（配置中的备用IP）

```python
def get_known_good_ips():
    """
    获取已知的可用IP列表（配置中的备用IP）

    Returns:
        list: 已知可用IP列表
    """
    pass
```

#### 4.2.2 fallback_dns_lookup

备用方案1: 尝试更多DNS服务器

```python
def fallback_dns_lookup():
    """
    备用方案1: 尝试更多DNS服务器

    Returns:
        list: DNS解析结果IP列表
    """
    pass
```

#### 4.2.3 fallback_known_ips

备用方案2: 使用已知的可用IP

```python
def fallback_known_ips():
    """
    备用方案2: 使用已知的可用IP

    Returns:
        list: 已知可用IP列表
    """
    pass
```

### 4.3 config_utils.py

配置工具模块，提供配置加载和路径获取功能。

#### 4.3.1 load_config

加载配置

```python
def load_config():
    """
    加载配置

    Returns:
        dict: 配置字典
    """
    pass
```

#### 4.3.2 get_hosts_path

获取hosts文件路径

```python
def get_hosts_path():
    """
    获取hosts文件路径

    Returns:
        Path: hosts文件路径对象
    """
    pass
```

### 4.4 connection_diagnostic_service.py

连接诊断服务，提供GitHub连接问题的详细诊断功能。

#### 4.4.1 diagnose_connection

诊断GitHub连接问题

```python
def diagnose_connection(progress_callback=None):
    """
    诊断GitHub连接问题

    Args:
        progress_callback: 进度回调函数

    Returns:
        dict: 诊断结果，包含local_network、github_status、dns_resolution、tcp_connection、http_response等字段
    """
    pass
```

#### 4.4.2 run_diagnosis

运行完整的连接诊断

```python
def run_diagnosis(progress_callback=None):
    """
    运行完整的连接诊断

    Args:
        progress_callback: 进度回调函数

    Returns:
        dict: 诊断结果
    """
    pass
```

### 4.5 fault_analysis_service.py

故障分析服务，提供复杂的故障分析和报告生成功能。

#### 4.5.1 analyze_fault_trends

分析故障趋势

```python
def analyze_fault_trends(days=30):
    """
    分析故障趋势

    Args:
        days: 分析天数，默认30天

    Returns:
        list: 故障趋势数据，包含每日故障数量、修复成功率等
    """
    pass
```

#### 4.5.2 analyze_fault_distribution

分析故障类型分布

```python
def analyze_fault_distribution(days=30):
    """
    分析故障类型分布

    Args:
        days: 分析天数，默认30天

    Returns:
        dict: 故障类型分布数据
    """
    pass
```

#### 4.5.3 generate_repair_report

生成详细的修复报告

```python
def generate_repair_report(repair_id=None, format="text"):
    """
    生成详细的修复报告

    Args:
        repair_id: 修复记录ID，None表示生成所有修复记录报告
        format: 报告格式，支持"text"和"json"

    Returns:
        str: 生成的修复报告
    """
    pass
```

### 4.6 guardian_utils.py

GitHub守护进程工具函数模块，提供守护进程相关的功能。

#### 4.6.1 save_state

保存状态到文件

```python
def save_state(state):
    """
    保存状态到文件

    Args:
        state: 要保存的状态字典
    """
    pass
```

#### 4.6.2 load_state

加载上次状态

```python
def load_state():
    """
    加载上次状态

    Returns:
        dict: 上次保存的状态字典
    """
    pass
```

#### 4.6.3 is_admin

检查是否具有管理员权限

```python
def is_admin():
    """
    检查是否具有管理员权限

    Returns:
        bool: 是否具有管理员权限
    """
    pass
```

### 4.7 ip_quality_service.py

IP质量服务，提供复杂的IP质量数据库管理和分析功能。

#### 4.7.1 analyze_ip_quality

分析单个IP的质量并更新数据库

```python
def analyze_ip_quality(ip, latency, success):
    """
    分析单个IP的质量并更新数据库

    Args:
        ip: 要分析的IP地址
        latency: 延迟时间（毫秒）
        success: 是否成功连接

    Returns:
        dict: 更新后的IP质量数据
    """
    pass
```

#### 4.7.2 get_top_ips

获取质量排名前N的IP

```python
def get_top_ips(count=5):
    """
    获取质量排名前N的IP

    Args:
        count: 要返回的IP数量，默认5个

    Returns:
        list: 质量排名前N的IP列表
    """
    pass
```

#### 4.7.3 generate_quality_report

生成完整的IP质量报告

```python
def generate_quality_report():
    """
    生成完整的IP质量报告

    Returns:
        dict: IP质量报告，包含总IP数、总测试数、平均成功率等
    """
    pass
```

## 5. trace层模块

### 5.1 fault_analysis.py

故障分析模块，提供故障记录和修复记录的管理功能。

#### 5.1.1 log_fault

记录故障信息

```python
def log_fault(fault_type, fault_name, details=None, latency=None):
    """
    记录故障信息

    Args:
        fault_type: 故障类型
        fault_name: 故障名称
        details: 故障详细信息
        latency: 延迟时间
    """
    pass
```

#### 5.1.2 log_repair

记录修复信息

```python
def log_repair(scheme, success, details=None, fault_type=None):
    """
    记录修复信息

    Args:
        scheme: 修复方案
        success: 是否修复成功
        details: 修复详细信息
        fault_type: 故障类型
    """
    pass
```

#### 5.1.3 load_fault_history

加载故障历史记录

```python
def load_fault_history():
    """
    加载故障历史记录

    Returns:
        list: 故障历史记录列表
    """
    pass
```

### 5.2 connection_diagnostic.py

连接诊断模块，提供网络连接诊断功能。

#### 5.2.1 get_known_good_ips

获取已知的可用IP列表

```python
def get_known_good_ips():
    """
    获取已知的可用IP列表

    Returns:
        list: 已知可用IP列表
    """
    pass
```

#### 5.2.2 test_single_ip

测试单个IP是否可用

```python
def test_single_ip(ip, port=443, timeout=2):
    """
    测试单个IP是否可用

    Args:
        ip: 要测试的IP地址
        port: 测试端口，默认443
        timeout: 超时时间，默认2秒

    Returns:
        bool: IP是否可用
    """
    pass
```

### 5.3 hosts_manager.py

Hosts管理模块，提供Hosts文件的读取、修改和备份功能。

#### 5.3.1 update_hosts

更新hosts文件

```python
def update_hosts(github_ips, backup=True):
    """
    更新hosts文件

    Args:
        github_ips: GitHub IP映射字典
        backup: 是否备份当前hosts文件

    Returns:
        dict: 操作结果
    """
    pass
```

#### 5.3.2 get_hosts_path

获取hosts文件路径

```python
def get_hosts_path():
    """
    获取hosts文件路径

    Returns:
        Path: hosts文件路径对象
    """
    pass
```

### 5.4 ip_quality_db.py

IP质量数据库模块，提供IP质量数据的存储和管理功能。

#### 5.4.1 load_ip_quality_db

加载IP质量数据库

```python
def load_ip_quality_db():
    """
    加载IP质量数据库

    Returns:
        dict: IP质量数据库
    """
    pass
```

#### 5.4.2 save_ip_quality

保存IP质量数据

```python
def save_ip_quality(ip, latency, success):
    """
    保存IP质量数据

    Args:
        ip: IP地址
        latency: 延迟时间
        success: 是否成功连接
    """
    pass
```

### 5.5 scheduled_inspection.py

定时检查模块，提供定时检查GitHub连接状态的功能。

#### 5.5.1 start_scheduled_inspection

启动定时检查

```python
def start_scheduled_inspection(interval=300):
    """
    启动定时检查

    Args:
        interval: 检查间隔，单位秒，默认300秒
    """
    pass
```

#### 5.5.2 stop_scheduled_inspection

停止定时检查

```python
def stop_scheduled_inspection():
    """
    停止定时检查
    """
    pass
```

## 6. 工具调用示例

### 6.1 调用连通性检测工具

```python
from github_utils import get_tool_config, run_tool

# 获取工具配置
checker_config = get_tool_config("checker")

# 运行工具
result = run_tool(checker_config)
print(result)
```

### 6.2 调用DNS查询工具

```python
from github_utils import get_tool_config, run_tool

# 获取工具配置
dns_config = get_tool_config("dns")

# 运行工具
result = run_tool(dns_config)
print(result)
```

### 6.3 调用IP测速工具

```python
from github_utils import get_tool_config, run_tool

# 获取工具配置
tester_config = get_tool_config("tester")

# 运行工具
result = run_tool(tester_config)
print(result)
```

### 6.4 调用一键修复工具

```python
from service.auto_diagnose_service import run as auto_diagnose_run

# 运行一键修复
result = auto_diagnose_run()
print(result)
```

### 6.5 调用故障分析工具

```python
from service.fault_analysis_service import analyze_fault_trends, generate_repair_report

# 分析故障趋势
fault_trends = analyze_fault_trends(days=7)
print("最近7天故障趋势:", fault_trends)

# 生成修复报告
report = generate_repair_report(format="json")
print("修复报告:", report)
```

## 7. 异步调用示例

```python
from github_utils import get_tool_config, AsyncTaskRunner

# 创建任务运行器
task_runner = AsyncTaskRunner(result_callback=lambda tool_key, status, data: print(f"{tool_key}: {status}, {data}"))

# 获取工具配置
tool_config = get_tool_config("checker")

# 异步运行工具
task_runner.run_tool_async("checker", tool_config, run_tool, button)
```

## 8. 配置文件结构

### 8.1 工具配置

```json
{
    "key": "checker",
    "name": "连通性检测",
    "description": "检测GitHub服务连接状态",
    "module": "github-checker-检测状态/github_checker.py",
    "function": "check"
}
```

### 8.2 子项目配置

```json
{
    "subprojects": {
        "GitHub-guardian-守护进程": {
            "name": "GitHub守护进程",
            "description": "监控并维护GitHub连接状态",
            "ip_pool": ["140.82.113.3", "140.82.114.3", "140.82.112.3"],
            "check_interval": 300,
            "timeout": 3
        }
    }
}
```

## 9. 错误处理

### 9.1 通用错误类型

| 错误类型          | 描述                             |
| ----------------- | -------------------------------- |
| ImportError       | 模块导入失败                     |
| FileNotFoundError | 配置文件或模块文件未找到         |
| PermissionError   | 权限不足，无法访问文件或执行操作 |
| ConnectionError   | 网络连接错误                     |
| TimeoutError      | 操作超时                         |

### 9.2 错误处理示例

```python
try:
    result = run_tool(tool_config)
except ImportError as e:
    print(f"模块导入失败: {e}")
except FileNotFoundError as e:
    print(f"文件未找到: {e}")
except PermissionError as e:
    print(f"权限不足: {e}")
except ConnectionError as e:
    print(f"网络连接错误: {e}")
except TimeoutError as e:
    print(f"操作超时: {e}")
except Exception as e:
    print(f"未知错误: {e}")
```

## 10. 性能优化建议

1. **并发测试**：使用多线程或异步方式并发测试多个IP，提高测速效率
2. **缓存结果**：对DNS解析结果和IP测速结果进行缓存，减少重复请求
3. **超时设置**：为网络请求设置合理的超时时间，避免长时间阻塞
4. **批量操作**：对相似操作进行批量处理，减少系统调用
5. **资源释放**：及时关闭文件和网络连接，释放系统资源

## 11. 扩展指南

### 11.1 添加新工具

1. 在对应目录创建工具Python文件
2. 在根目录 `config.json` 的 `tools` 数组中注册工具
3. 添加工具信息包括：key（唯一标识）、name（显示名称）、description（功能描述）、module（模块路径）、function（入口函数）

### 11.2 自定义UI组件

1. 继承现有UI组件类
2. 重写需要自定义的方法
3. 在主界面中使用自定义组件

### 11.3 添加新功能模块

1. 在 `github_utils` 目录下创建新的模块文件
2. 实现新功能
3. 在 `__init__.py` 中导出新功能
4. 在其他模块中导入并使用

## 12. 版本兼容性

| Python版本  | 兼容性      |
| ----------- | ----------- |
| Python 3.8  | ✅ 完全兼容 |
| Python 3.9  | ✅ 完全兼容 |
| Python 3.10 | ✅ 完全兼容 |
| Python 3.11 | ✅ 完全兼容 |
| Python 3.12 | ✅ 完全兼容 |

## 13. 依赖说明

本项目主要依赖Python标准库，无需额外安装第三方库：

- `tkinter`：图形界面（Python内置）
- `json`：配置文件处理（Python内置）
- `socket`：网络连接测试（Python内置）
- `threading`：多线程处理（Python内置）
- `queue`：任务队列管理（Python内置）
- `time`：时间处理（Python内置）
- `os`：操作系统交互（Python内置）
- `sys`：系统相关功能（Python内置）
- `pathlib`：路径处理（Python内置）
- `importlib`：动态模块加载（Python内置）
- `inspect`：函数签名检查（Python内置）

## 14. 调试技巧

### 14.1 启用调试模式

在 `config.json` 中添加调试配置：

```json
{
    "debug": true
}
```

### 14.2 打印调试信息

使用Python内置的 `logging` 模块打印调试信息：

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logging.debug("调试信息")
logging.info("普通信息")
logging.warning("警告信息")
logging.error("错误信息")
logging.critical("严重错误")
```

### 14.3 使用pdb调试

```python
import pdb

# 在需要调试的位置添加
pdb.set_trace()
```

## 15. 测试建议

### 15.1 单元测试

使用Python内置的 `unittest` 或 `pytest` 框架编写单元测试：

```python
import unittest
from github_utils import common_utils

class TestCommonUtils(unittest.TestCase):
    def test_load_sub_config(self):
        config = common_utils.load_sub_config("GitHub-guardian-守护进程")
        self.assertIsInstance(config, dict)
        self.assertIn("ip_pool", config)

if __name__ == "__main__":
    unittest.main()
```

### 15.2 集成测试

编写集成测试，测试整个工具链：

```python
from github_utils import get_tool_config, run_tool

# 测试连通性检测
def test_checker():
    checker_config = get_tool_config("checker")
    result = run_tool(checker_config)
    assert result["status"] in ["good", "warn", "bad"]

# 测试DNS查询
def test_dns():
    dns_config = get_tool_config("dns")
    result = run_tool(dns_config)
    assert isinstance(result, list)
    assert len(result) > 0

# 运行测试
test_checker()
test_dns()
print("所有测试通过")
```

## 16. 部署指南

### 16.1 本地部署

1. 克隆或下载项目到本地
2. 确保Python 3.8+已安装
3. 直接运行，无需额外安装依赖

### 16.2 打包成可执行文件

使用PyInstaller打包成可执行文件：

```bash
# 安装PyInstaller
pip install pyinstaller

# 打包主界面
pyinstaller --onefile --windowed --name="GitHub工具合集" main_gui.py

# 打包命令行工具
pyinstaller --onefile --name="github_auto_diagnose" trace/auto_diagnose.py
```

### 16.3 定时任务部署

使用Windows任务计划程序设置定时任务：

1. 打开"任务计划程序"
2. 点击"创建基本任务"
3. 填写任务名称和描述
4. 设置触发条件（如每天、每小时等）
5. 设置操作（启动程序）
6. 选择Python解释器和脚本路径
7. 完成任务创建

## 17. 常见问题

### 17.1 权限不足

**问题**：运行Hosts修复工具时提示权限不足

**解决方案**：以管理员身份运行命令提示符或PowerShell，然后执行脚本

### 17.2 网络连接失败

**问题**：DNS查询或IP测速失败

**解决方案**：

1. 检查网络连接是否正常
2. 检查防火墙设置，确保Python解释器具有网络访问权限
3. 尝试更换DNS服务器

### 17.3 Hosts文件修改失败

**问题**：无法修改Hosts文件

**解决方案**：

1. 确保以管理员身份运行
2. 检查Hosts文件是否被其他程序占用
3. 检查Hosts文件权限设置

### 17.4 图形界面无法启动

**问题**：运行main_gui.py时提示tkinter模块未找到

**解决方案**：

1. 确保Python安装了tkinter模块
2. 对于Windows系统，tkinter通常是内置的
3. 对于Linux系统，可能需要安装：`sudo apt-get install python3-tk`

## 18. 技术支持

### 18.1 问题反馈

如果您在使用过程中遇到问题，请通过以下方式反馈：

- 提交GitHub Issue
- 发送邮件到项目维护者
- 参与项目讨论

### 18.2 贡献代码

欢迎您为项目贡献代码：

1. Fork项目
2. 创建功能分支
3. 提交代码
4. 创建Pull Request

### 18.3 文档贡献

欢迎您改进项目文档：

1. 修正文档中的错误
2. 补充缺失的内容
3. 优化文档结构
4. 翻译文档

## 19. 许可证

本项目采用MIT许可证，详情请见LICENSE文件。

## 20. 更新日志

### v1.1.0 (2025-12-30)

- 移除 `GitHub-main-主界面/` 目录，配置统一到根目录
- 新增 `design.txt`、`design.txt.bak`、`style.md`、`project_rule.md` 文件
- 各子模块添加独立配置文件
- 更新项目结构和文档说明

### v1.0.0 (2025-12-29)

- 初始版本发布
- 图形界面整合
- 模块化重构
- 完整代码风格检查

## 21. 致谢

感谢所有为项目做出贡献的开发者和用户！

## 22. 免责声明

本工具仅供学习和技术研究使用。请遵守GitHub服务条款和当地法律法规。作者不对因使用本工具造成的任何损失承担责任。
