# GitHub工具合集 - API文档

## 概述

本项目提供了一系列用于优化GitHub访问的Python工具，包含连接检测、DNS查询、IP测速、Hosts修复、系统诊断和实时守护等功能。

## 模块结构

```
github_utils/
├── __init__.py
├── common_utils.py    # 通用工具函数
├── async_utils.py     # 异步任务处理
└── gui_utils.py       # GUI构建工具
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

## 4. 工具调用示例

### 4.1 调用连通性检测工具

```python
from github_utils import get_tool_config, run_tool

# 获取工具配置
checker_config = get_tool_config("checker")

# 运行工具
result = run_tool(checker_config)
print(result)
```

### 4.2 调用DNS查询工具

```python
from github_utils import get_tool_config, run_tool

# 获取工具配置
dns_config = get_tool_config("dns")

# 运行工具
result = run_tool(dns_config)
print(result)
```

### 4.3 调用IP测速工具

```python
from github_utils import get_tool_config, run_tool

# 获取工具配置
tester_config = get_tool_config("tester")

# 运行工具
result = run_tool(tester_config)
print(result)
```

## 5. 异步调用示例

```python
from github_utils import get_tool_config, AsyncTaskRunner

# 创建任务运行器
task_runner = AsyncTaskRunner(result_callback=lambda tool_key, status, data: print(f"{tool_key}: {status}, {data}"))

# 获取工具配置
tool_config = get_tool_config("checker")

# 异步运行工具
task_runner.run_tool_async("checker", tool_config, run_tool, button)
```

## 6. 配置文件结构

### 6.1 工具配置

```json
{
  "key": "checker",
  "name": "连通性检测",
  "description": "检测GitHub服务连接状态",
  "module": "github-checker-检测状态/github_checker.py",
  "function": "check"
}
```

### 6.2 子项目配置

```json
{
  "subprojects": {
    "GitHub-guardian-守护进程": {
      "name": "GitHub守护进程",
      "description": "监控并维护GitHub连接状态",
      "ip_pool": [
        "140.82.113.3",
        "140.82.114.3",
        "140.82.112.3"
      ],
      "check_interval": 300,
      "timeout": 3
    }
  }
}
```

## 7. 错误处理

### 7.1 通用错误类型

| 错误类型 | 描述 |
|----------|------|
| ImportError | 模块导入失败 |
| FileNotFoundError | 配置文件或模块文件未找到 |
| PermissionError | 权限不足，无法访问文件或执行操作 |
| ConnectionError | 网络连接错误 |
| TimeoutError | 操作超时 |

### 7.2 错误处理示例

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

## 8. 性能优化建议

1. **并发测试**：使用多线程或异步方式并发测试多个IP，提高测速效率
2. **缓存结果**：对DNS解析结果和IP测速结果进行缓存，减少重复请求
3. **超时设置**：为网络请求设置合理的超时时间，避免长时间阻塞
4. **批量操作**：对相似操作进行批量处理，减少系统调用
5. **资源释放**：及时关闭文件和网络连接，释放系统资源

## 9. 扩展指南

### 9.1 添加新工具

1. 在对应目录创建工具Python文件
2. 在根目录 `config.json` 的 `tools` 数组中注册工具
3. 添加工具信息包括：key（唯一标识）、name（显示名称）、description（功能描述）、module（模块路径）、function（入口函数）

### 9.2 自定义UI组件

1. 继承现有UI组件类
2. 重写需要自定义的方法
3. 在主界面中使用自定义组件

### 9.3 添加新功能模块

1. 在 `github_utils` 目录下创建新的模块文件
2. 实现新功能
3. 在 `__init__.py` 中导出新功能
4. 在其他模块中导入并使用

## 10. 版本兼容性

| Python版本 | 兼容性 |
|------------|--------|
| Python 3.8 | ✅ 完全兼容 |
| Python 3.9 | ✅ 完全兼容 |
| Python 3.10 | ✅ 完全兼容 |
| Python 3.11 | ✅ 完全兼容 |
| Python 3.12 | ✅ 完全兼容 |

## 11. 依赖说明

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

## 12. 调试技巧

### 12.1 启用调试模式

在 `config.json` 中添加调试配置：

```json
{
  "debug": true
}
```

### 12.2 打印调试信息

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

### 12.3 使用pdb调试

```python
import pdb

# 在需要调试的位置添加
pdb.set_trace()
```

## 13. 测试建议

### 13.1 单元测试

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

### 13.2 集成测试

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

## 14. 部署指南

### 14.1 本地部署

1. 克隆或下载项目到本地
2. 确保Python 3.8+已安装
3. 直接运行，无需额外安装依赖

### 14.2 打包成可执行文件

使用PyInstaller打包成可执行文件：

```bash
# 安装PyInstaller
pip install pyinstaller

# 打包主界面
pyinstaller --onefile --windowed --name="GitHub工具合集" main_gui.py

# 打包命令行工具
pyinstaller --onefile --name="github_auto_diagnose" trace/auto_diagnose.py
```

### 14.3 定时任务部署

使用Windows任务计划程序设置定时任务：

1. 打开"任务计划程序"
2. 点击"创建基本任务"
3. 填写任务名称和描述
4. 设置触发条件（如每天、每小时等）
5. 设置操作（启动程序）
6. 选择Python解释器和脚本路径
7. 完成任务创建

## 15. 常见问题

### 15.1 权限不足

**问题**：运行Hosts修复工具时提示权限不足

**解决方案**：以管理员身份运行命令提示符或PowerShell，然后执行脚本

### 15.2 网络连接失败

**问题**：DNS查询或IP测速失败

**解决方案**：
1. 检查网络连接是否正常
2. 检查防火墙设置，确保Python解释器具有网络访问权限
3. 尝试更换DNS服务器

### 15.3 Hosts文件修改失败

**问题**：无法修改Hosts文件

**解决方案**：
1. 确保以管理员身份运行
2. 检查Hosts文件是否被其他程序占用
3. 检查Hosts文件权限设置

### 15.4 图形界面无法启动

**问题**：运行main_gui.py时提示tkinter模块未找到

**解决方案**：
1. 确保Python安装了tkinter模块
2. 对于Windows系统，tkinter通常是内置的
3. 对于Linux系统，可能需要安装：`sudo apt-get install python3-tk`

## 16. 技术支持

### 16.1 问题反馈

如果您在使用过程中遇到问题，请通过以下方式反馈：

- 提交GitHub Issue
- 发送邮件到项目维护者
- 参与项目讨论

### 16.2 贡献代码

欢迎您为项目贡献代码：

1. Fork项目
2. 创建功能分支
3. 提交代码
4. 创建Pull Request

### 16.3 文档贡献

欢迎您改进项目文档：

1. 修正文档中的错误
2. 补充缺失的内容
3. 优化文档结构
4. 翻译文档

## 17. 许可证

本项目采用MIT许可证，详情请见LICENSE文件。

## 18. 更新日志

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

## 19. 致谢

感谢所有为项目做出贡献的开发者和用户！

## 20. 免责声明

本工具仅供学习和技术研究使用。请遵守GitHub服务条款和当地法律法规。作者不对因使用本工具造成的任何损失承担责任。
