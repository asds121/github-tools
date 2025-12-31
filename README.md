# GitHub工具合集

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)]()

GitHub工具合集 - 一站式GitHub访问优化解决方案，包含连接检测、DNS查询、IP测速、Hosts修复、系统诊断和实时守护等功能。

## 功能特性

- **一键检测修复**：自动检测GitHub连接状态，若异常则自动进行DNS解析、IP测速、Hosts修复并验证结果
- **Hosts修复**：自动修改系统Hosts文件，绑定GitHub域名到最优IP
- **DNS查询**：通过多个DNS服务器查询GitHub域名的IP地址
- **IP测速**：并发测试多个GitHub IP的连接速度，筛选最优IP
- **守护进程**：实时监控GitHub连接状态，自动修复Hosts文件
- **图形界面**：Tkinter GUI整合所有功能，一站式操作

## 项目结构

```
github工具合集/
├── GitHub-guardian-守护进程/          # 守护进程模块
│   ├── config.json                   # 守护进程配置
│   └── github_guardian_ascii.py
├── GitHub-hosts-viewer-查看/          # Hosts查看模块
│   └── github_hosts_viewer.py
├── GitHub-repair-fix-修复/            # Hosts修复模块
│   ├── config.json                   # 修复工具配置
│   └── github_repair_fix.py
├── GitHub-searcher-dns-DNS/           # DNS查询模块
│   ├── config.json                   # DNS工具配置
│   └── github_dns.py
├── GitHub-searcher-test-测速/          # IP测速模块
│   ├── config.json                   # 测速工具配置
│   └── github_ip_tester.py
├── github-checker-检测状态/            # 连通性检测（独立项目）
│   ├── LICENSE
│   ├── README.md
│   ├── github_checker.py
│   ├── start-full.bat
│   └── start.bat
├── github_utils/                      # 公共工具模块
│   ├── __init__.py
│   ├── common_utils.py                # 通用工具函数
│   ├── async_utils.py                 # 异步任务处理
│   └── gui_utils.py                   # GUI构建工具
├── service/                           # 业务逻辑服务层
│   ├── auto_diagnose_fallbacks.py     # 一键诊断备用方案
│   ├── config_utils.py                # 配置工具模块
│   ├── data_statistics_analysis.py    # 数据统计分析
│   ├── data_statistics_specific.py    # 特定统计方法
│   ├── data_statistics_utils.py       # 数据统计工具
│   ├── guardian_utils.py              # 守护进程工具
│   ├── scheduled_inspection_cli.py    # 定时巡检命令行
│   ├── scheduled_inspection_stats.py  # 定时巡检统计
│   └── scheduled_inspection_utils.py  # 定时巡检工具
├── trace/                             # 追踪和监控功能层
│   ├── __init__.py
│   ├── auto_diagnose.py               # 自动诊断
│   ├── connection_diagnostic.py       # 连接诊断
│   ├── data_statistics.py             # 数据统计
│   ├── dns_explorer.py                # DNS探索
│   ├── guardian_state.json            # 守护进程状态
│   ├── hosts_manager.py               # Hosts管理器
│   ├── ip_blacklist.py                # IP黑名单
│   ├── ip_quality_db.json             # IP质量数据库
│   ├── ip_quality_db.py               # IP质量数据库管理
│   ├── ip_speed_ranking.py            # IP速度排名
│   ├── quick_speed_test.py            # 快速测速
│   └── scheduled_inspection.py        # 定时巡检
├── main_gui.py                        # GUI主程序
├── config.json                        # 项目配置（工具列表和UI设置）
├── .flake8                            # Flake8代码风格配置
├── .gitignore                         # Git忽略文件配置
├── .editorconfig                      # 编辑器配置
├── pyproject.toml                     # Python项目配置
├── LICENSE                            # MIT许可证
├── README.md                          # 项目文档
├── start.bat                          # 启动脚本
├── style.md                           # 代码风格规范
├── project_rule.md                    # 项目规则说明
```

## 快速开始

### 环境要求

- 操作系统：Windows 7/10/11
- Python版本：Python 3.8+
- 依赖：tkinter（Python内置）

### 安装方法

1. 克隆或下载项目到本地
2. 确保Python 3.8+已安装
3. 直接运行，无需额外安装依赖

### 运行方式

#### 图形界面（推荐）

双击运行 `start.bat` 或执行：

```bash
python main_gui.py
```

#### 命令行工具

```bash
# 一键检测修复
python trace/auto_diagnose.py

# 快速测速
python trace/quick_speed_test.py

# Hosts管理器
python trace/hosts_manager.py

# 连接诊断
python trace/connection_diagnostic.py

# IP黑名单管理
python trace/ip_blacklist.py

# DNS查询
python GitHub-searcher-dns-DNS/github_dns.py

# IP测速
python GitHub-searcher-test-测速/github_ip_tester.py

# Hosts修复
python GitHub-repair-fix-修复/github_repair_fix.py

# 启动守护进程
python GitHub-guardian-守护进程/github_guardian_ascii.py

# 查看Hosts配置
python GitHub-hosts-viewer-查看/github_hosts_viewer.py
```

## 工具说明

### 主界面 [main_gui.py](file:///c:/Users/Administrator/Desktop/代码/github工具合集/main_gui.py)

**文件：** `main_gui.py`

图形界面整合所有功能，包含两个功能标签页：

- **工具**：显示所有可用工具按钮，点击执行对应功能
- **说明**：显示各工具的功能说明和使用推荐

### 连通性检测 [github-checker-检测状态](file:///c:/Users/Administrator/Desktop/代码/github工具合集/github-checker-检测状态)

**文件：** `github_checker.py`

快速检测GitHub服务连接状态。

```bash
python github_checker.py        # 快速检测
python github_checker.py -f     # 完整测试（3次迭代）
```

### DNS查询 [GitHub-searcher-dns-DNS](file:///c:/Users/Administrator/Desktop/代码/github工具合集/GitHub-searcher-dns-DNS)

**文件：** `github_dns.py`

通过多个DNS服务器查询GitHub域名的IP地址。

### IP测速 [GitHub-searcher-test-测速](file:///c:/Users/Administrator/Desktop/代码/github工具合集/GitHub-searcher-test-测速)

**文件：** `github_ip_tester.py`

并发测试多个GitHub IP的连接速度，自动筛选最优IP。

### Hosts修复 [GitHub-repair-fix-修复](file:///c:/Users/Administrator/Desktop/代码/github工具合集/GitHub-repair-fix-修复)

**文件：** `github_repair_fix.py`

修改系统Hosts文件，绑定GitHub域名到最优IP，绕过DNS污染。

**注意：** 需要管理员权限运行。

### Hosts查看 [GitHub-hosts-viewer-查看](file:///c:/Users/Administrator/Desktop/代码/github工具合集/GitHub-hosts-viewer-查看)

**文件：** `github_hosts_viewer.py`

查看当前系统Hosts文件配置（忽略注释）。

### 守护进程 [GitHub-guardian-守护进程](file:///c:/Users/Administrator/Desktop/代码/github工具合集/GitHub-guardian-守护进程)

**文件：** `github_guardian_ascii.py`

实时监控GitHub连接状态，当检测到断连时自动修复Hosts文件。

### 公共模块 [github_utils](file:///c:/Users/Administrator/Desktop/代码/github工具合集/github_utils)

为GUI主界面提供的公共功能模块：

- `common_utils.py`：通用工具函数
- `async_utils.py`：异步任务处理
- `gui_utils.py`：GUI构建工具
- `__init__.py`：模块导出

## 配置说明

### 配置文件

项目使用根目录的 `config.json` 进行统一配置，包含工具列表定义和GUI界面设置：

```json
{
    "tools": [
        {
            "key": "checker",
            "name": "连通性检测",
            "description": "检测GitHub服务连接状态",
            "module": "github-checker-检测状态/github_checker.py",
            "function": "check"
        },
        {
            "key": "dns",
            "name": "DNS查询",
            "description": "从DNS服务器获取GitHub的IP地址",
            "module": "GitHub-searcher-dns-DNS/github_dns.py",
            "function": "resolve_all"
        }
        // ... 更多工具配置
    ],
    "ui": {
        "window": {
            "title": "GitHub工具合集 - 主界面",
            "size": "500x650"
        }
        // ... UI样式配置
    }
}
```

## 代码风格

本项目遵循PEP8代码风格，使用flake8进行代码检查。

### 检查代码

```bash
# 检查整个项目（忽略特定目录）
python -m flake8 . --exclude=github-checker-检测状态
```

### 配置文件

`.flake8` 文件包含项目特定的代码风格规则：

```ini
[flake8]
max-line-length = 120
exclude = .git,__pycache__,trace,github-checker-检测状态
per-file-ignores =
    __init__.py: F401
```

## 技术原理

### Hosts文件修改

通过修改 `C:\Windows\System32\drivers\etc\hosts` 文件，直接将GitHub域名绑定到最优IP地址，绕过DNS污染，获得更稳定快速的访问体验。

### DNS解析优化

使用多个DNS服务器（如223.5.5.5、8.8.8.8）进行查询，对比结果获取最准确的IP地址。

### IP智能测试

使用多线程并发测试多个IP地址的连接延迟，自动筛选出响应最快的IP，确保最佳访问速度。

### 连接监控

守护进程定时检测GitHub连接状态，一旦发现连接失败，立即自动修复Hosts文件，实现无人值守的运维体验。

## 开发指南

### 添加新工具

1. 在对应目录创建工具Python文件
2. 在根目录 `config.json` 的 `tools` 数组中注册工具
3. 添加工具信息包括：key（唯一标识）、name（显示名称）、description（功能描述）、module（模块路径）、function（入口函数）

### 代码规范

- 遵循PEP8代码风格
- 函数添加清晰的文档字符串
- 使用英语或中文注释（保持一致）
- 行长度限制：120字符

### 项目配置

`pyproject.toml` 文件定义了项目元数据和构建配置，`style.md` 文件定义了代码风格规范，`project_rule.md` 文件定义了项目规则说明。

## 注意事项

### 权限要求

Hosts修复工具需要管理员权限。请以管理员身份运行命令提示符或PowerShell。

### 自动备份

Hosts修复工具会自动创建备份文件（`hosts.bak`），如需恢复可手动操作。

### 防火墙设置

确保Python解释器具有网络访问权限，以便进行IP测试和DNS查询。

### 目录说明

- `github-checker-检测状态/` - 保持原样，不做修改（独立子项目）
- `trace/` - 一键诊断和测速功能模块
- `github_utils/` - GUI公共工具模块

## 版本历史

### v1.1.2 (2025-12-31)

- 将github-checker.py的行数从139行减少到70行，符合120行以内的要求
- 为所有service层文件添加了对trace层内容的引用，符合分层架构要求
- 更新了.gitignore文件，添加了忽略txt文件的规则
- 更新了项目结构文档，添加了service层和trace层的详细信息

### v1.1.1 (2025-12-30)

- 修复了守护进程中未使用的`global running`变量
- 修复了HOSTS修复工具中的变量名`l`为`line`，避免歧义
- 修复了多个文件中的裸except问题，改为使用`except Exception:`
- 修复了HOSTS查看器中的无效转义序列问题，使用原始字符串表示路径
- 修复了测速工具中未使用的`load_ip_quality_db`导入
- 更新了flake8配置，忽略更多非关键警告
- 优化了代码风格检查配置
- 改进了进度条清理逻辑，避免残留字符
- 增强了结果面板的稳定性
- 添加了API文档（API.md），详细说明了模块和函数的使用方法
- 添加了GitHub Actions配置，实现自动CI/CD流程

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

## 许可证

本项目采用MIT许可证。

## 免责声明

本工具仅供学习和技术研究使用。请遵守GitHub服务条款和当地法律法规。作者不对因使用本工具造成的任何损失承担责任。

## 更新日期

2025-12-31
