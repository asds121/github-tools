# GitHub Tools 代码风格规范
# 基于 github-checker 分析生成
# 原则：github-checker 允许的，其他项目也允许；github-checker 没有的，其他项目也不要求

## 1. 文件头

### 编码声明
- 可选（github-checker 有 `# -*- coding: ascii -*-`）

### Shebang
- 可选（github-checker 没有 shebang，直接以编码声明开头）

### 文档字符串
- 必须有
- 格式：`"""模块名 - 功能描述"""`
- 使用双引号
- 首行大写，简洁描述模块功能

## 2. 导入组织

### 标准库顺序
1. 标准库导入
2. 第三方库导入
3. 本地模块导入

### 示例
```python
import sys
import time
import threading
from queue import Queue
import urllib.request
```

## 3. 命名规范

### 常量
- 命名：UPPERCASE_WITH_UNDERSCORES
- 示例：`DEFAULT_TIMEOUT = 8.0`、`THRESHOLD_MS = 3000`

### 变量
- 命名：snake_case（小写字母加下划线）
- 示例：`stop_event`、`queue`

### 函数
- 命名：snake_case（小写字母加下划线）
- 示例：`test_url()`、`check_single()`

### 类名（如使用）
- 命名：PascalCase（大驼峰）
- 示例：`class GitHubChecker:`（如需要面向对象）

## 4. 空格规范

### 操作符周围
- 运算符两侧加空格：`a + b`、`x = 5`
- 关键字参数不加空格：`function(arg=value)`

### 函数调用
- 逗号后加空格：`test_url(url, timeout)`
- 无多余空格：`f"Status: {status}"`

### 赋值语句
- `=` 周围加空格（除非是关键字参数）

## 5. 行长度

- 单行不超过 120 字符
- 长表达式使用括号换行

## 6. 缩进

- 使用 4 个空格缩进
- 不使用 Tab

## 7. 空行

- 函数定义之间：2 行空行
- 函数内部逻辑分段：1 行空行
- 文件末尾：无需空行

## 8. 字符串

### 字符串引号
- 优先使用双引号：`"string"`
- 字符串内含双引号时使用单引号：`'He said: "hello"'`

### 字符串格式化
- 优先使用 f-string：`f"Status: {status}"`
- 简单拼接使用 `+` 运算符

## 9. 异常处理

- 允许使用裸 `except:`（github-checker 使用裸 except）
- 其他写法也允许

## 10. 控制流

### if 语句
```python
if condition:
    do_something()
else:
    do_other()
```

### 循环
```python
for name, url in TARGETS:
    # code
```

### 字典/列表推导式
- 复杂逻辑拆分为多行或普通循环
- 简单推导式可单行：`[x for x in items if x > 0]`

## 11. 主入口

### 使用主守卫
```python
if __name__ == "__main__":
    main()
```

## 12. 注释

- 避免多余注释
- 复杂逻辑可添加注释说明
- 行内注释在代码后加 2 个空格再添加

## 13. 函数设计

### 单一职责
- 每个函数只做一件事
- 函数长度控制在合理范围（建议不超过 50 行）

### 参数
- 避免过多参数（超过 4 个考虑封装为字典或类）
- 使用关键字参数提高可读性

## 14. 返回值

- 函数返回值类型保持一致
- 复杂结果使用字典返回：`return {"status": status, "ms": avg_ms, "results": results}`

## 15. 代码示例

```python
#!/usr/bin/env python3
"""GitHub Checker - Check GitHub accessibility"""

import sys
import time
import urllib.request

TARGETS = [
    ("homepage", "https://github.com"),
    ("api", "https://api.github.com"),
]
DEFAULT_TIMEOUT = 8.0
THRESHOLD_MS = 3000


def test_url(url, timeout):
    try:
        start = time.time()
        req = urllib.request.Request(url, headers={"User-Agent": "GitHubChecker/2.0"})
        response = urllib.request.urlopen(req, timeout=timeout)
        response.read()
        ms = round((time.time() - start) * 1000)
        return {"ok": response.status == 200, "ms": ms}
    except:
        return {"ok": False, "ms": 0}


def check_single():
    results = []
    for name, url in TARGETS:
        result = test_url(url, DEFAULT_TIMEOUT)
        results.append((name, result))
        if name == "homepage" and not result["ok"]:
            break

    avg_ms = sum(r[1]["ms"] for r in results) / len(results)

    if all(r[1]["ok"] for r in results):
        status = "good" if avg_ms < THRESHOLD_MS else "warn"
    else:
        status = "bad"

    return {"status": status, "ms": avg_ms, "results": results}


def main():
    result = check_single()
    status = result["status"].upper()
    suffix = f" ({result['ms']:.0f}ms)" if result["status"] != "bad" else ""
    print(f"\nStatus: {status}{suffix}")


if __name__ == "__main__":
    main()
```

## 16. 快速检查清单
- [ ] 有模块文档字符串
- [ ] 常量使用 UPPER_CASE
- [ ] 变量和函数使用 snake_case
- [ ] 运算符周围有空格
- [ ] 逗号后有空格
- [ ] 使用 4 空格缩进
- [ ] 字符串使用 f-string 或双引号
- [ ] 有主入口守卫（如果需要）
- [ ] 无过长行
