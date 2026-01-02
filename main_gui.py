#!/usr/bin/env python3
"""GitHub工具合集 - 主界面"""
import sys
import json
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tkinter import ttk, Canvas  # noqa: E402
from github_utils import (  # noqa: E402
    get_tools_order, get_tool_config, run_tool,
    Tooltip, AsyncTaskRunner, ResultPanel,
    create_main_window, setup_window_style, create_notebook, create_tab,
    create_button_panel, create_exit_button
)
from github_utils.common_utils import load_module

# 加载网络检测模块
checker_module = load_module(
    Path(__file__).resolve().parent / "github-checker-检测状态" / "github_checker.py"
)
check_github = checker_module.check

CONFIG_PATH = Path(__file__).resolve().parent / "config.json"
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

UI_CONFIG = CONFIG["ui"]
TOOLS_ORDER = get_tools_order()
layout_cfg = UI_CONFIG["layout"]
text_cfg = UI_CONFIG["text"]


class ToolButton(ttk.Button):
    def __init__(self, parent, tool_key, run_async):
        self.tool_key = tool_key
        tool_config = get_tool_config(tool_key)
        super().__init__(parent, text=tool_config["name"],
                         command=lambda: run_async(tool_key, self),
                         width=layout_cfg["tool_button_width"])


class NetworkIndicator(Canvas):
    """网络状态指示灯"""
    def __init__(self, parent, size=20, **kwargs):
        super().__init__(parent, width=size, height=size, **kwargs)
        self.size = size
        self.status = "offline"  # online, offline, testing
        self.draw()
    
    def draw(self):
        """绘制指示灯"""
        self.delete("all")
        
        # 定义颜色
        colors = {
            "online": "#4CAF50",  # 绿色 - 在线
            "offline": "#F44336",  # 红色 - 离线
            "testing": "#FFC107"   # 黄色 - 测试中
        }
        
        # 绘制圆形指示灯
        self.create_oval(2, 2, self.size-2, self.size-2, 
                        fill=colors[self.status], outline="black", width=1)
    
    def set_status(self, status):
        """设置指示灯状态"""
        self.status = status
        self.draw()
    
    def update_status(self, result):
        """根据检测结果更新状态"""
        if result["status"] == "good":
            self.set_status("online")
        else:
            self.set_status("offline")


def main():
    root = create_main_window()
    setup_window_style(root)
    
    # 创建标题和网络状态指示区域
    header_frame = ttk.Frame(root)
    header_frame.pack(fill="x", pady=(UI_CONFIG["padding"]["title_pady_top"],
                                      UI_CONFIG["padding"]["title_pady_bottom"]))
    
    # 主标题
    ttk.Label(header_frame, text=text_cfg["main_title"],
              style="Title.TLabel").pack(side="left")
    
    # 网络状态指示灯
    status_frame = ttk.Frame(header_frame)
    status_frame.pack(side="right")
    
    ttk.Label(status_frame, text="网络状态: ").pack(side="left", padx=(0, 5))
    network_indicator = NetworkIndicator(status_frame, size=20, relief="raised")
    network_indicator.pack(side="left")
    
    # 最后检测时间标签
    last_check_label = ttk.Label(status_frame, text="最后检测: 从未")
    last_check_label.pack(side="left", padx=(10, 0))

    notebook = create_notebook(root, UI_CONFIG)
    tools_frame = create_tab(notebook, UI_CONFIG["tabs"]["tools_text"],
                             UI_CONFIG["padding"]["tab_padding"])
    info_frame = create_tab(notebook, UI_CONFIG["tabs"]["info_text"],
                            UI_CONFIG["padding"]["tab_padding"])

    btn_panel = create_button_panel(tools_frame)
    btn_panel.pack(fill="x", pady=(0, 10))

    result_panel = ResultPanel(tools_frame, UI_CONFIG, layout_cfg)
    result_text = result_panel.text
    
    # 网络检测结果显示
    network_status_text = result_text
    
    # 定时网络检测函数
    def check_network_status():
        """检测网络状态并更新指示灯"""
        network_indicator.set_status("testing")
        try:
            result = check_github()
            current_time = time.strftime("%H:%M:%S")
            network_indicator.update_status(result)
            last_check_label.config(text=f"最后检测: {current_time}")
            
            # 记录检测结果
            network_status_text.insert("end", f"\n[{current_time}] 网络检测: {result['status']} - {result.get('message', '')}")
            network_status_text.see("end")
        except Exception as e:
            network_indicator.set_status("offline")
            last_check_label.config(text=f"最后检测: 失败")
            network_status_text.insert("end", f"\n[{time.strftime('%H:%M:%S')}] 网络检测失败: {str(e)}")
            network_status_text.see("end")
    
    # 定时检测线程
    def start_network_monitor():
        """启动定时网络检测"""
        while True:
            check_network_status()
            time.sleep(180)  # 每3分钟检测一次
    
    # 启动检测线程
    monitor_thread = threading.Thread(target=start_network_monitor, daemon=True)
    monitor_thread.start()

    ttk.Label(info_frame, text=text_cfg["info_frame_title"],
              font=tuple(UI_CONFIG["style"]["label_font"])).pack(
                  anchor="w",
                  pady=(0, UI_CONFIG["padding"]["info_title_pady_bottom"]))
    ttk.Label(info_frame, text=text_cfg["info_content"],
              justify="left",
              foreground=UI_CONFIG["colors"]["info_text_foreground"]).pack(
                  anchor="w")

    def handle_result(tool_key, status, data):
        result_panel.clear_progress()
        if status == "success":
            result_text.insert("end", json.dumps(data, ensure_ascii=False,
                                                 indent=2) + "\n")
        else:
            result_text.insert("end", f"错误: {data}\n")
        result_text.see("end")

    task_runner = AsyncTaskRunner(result_callback=handle_result)

    def run_tool_async(tool_key, btn):
        tool_config = get_tool_config(tool_key)
        result_panel.clear_progress()
        result_text.insert("end", f"\n{'=' * 40}\n")
        result_text.insert("end", f"正在执行: {tool_config['name']}...\n")
        result_text.see("end")
        output_func = result_panel.create_progress_output_func()
        if output_func is not None:
            task_runner.run_tool_async(tool_key, tool_config, run_tool, btn,
                                       output_func=output_func)
        else:
            task_runner.run_tool_async(tool_key, tool_config, run_tool, btn)
        root.after(100, check_queue)

    def check_queue():
        if task_runner.check_queue(list(tool_buttons.values())):
            root.after(100, check_queue)

    tool_buttons = {}
    for i, key in enumerate(TOOLS_ORDER):
        row = i // layout_cfg["buttons_per_row"]
        col = i % layout_cfg["buttons_per_row"]
        btn = ToolButton(btn_panel, key, run_tool_async)
        btn.grid(row=row, column=col,
                 padx=layout_cfg["button_padding_x"],
                 pady=layout_cfg["button_padding_y"],
                 sticky="w")
        tool_buttons[key] = btn
        Tooltip(btn, get_tool_config(key)["description"], UI_CONFIG)

    exit_btn = create_exit_button(btn_panel, root.destroy, UI_CONFIG)
    exit_btn.grid(row=0, column=layout_cfg["exit_button_column"],
                  padx=layout_cfg["button_padding_x"],
                  pady=layout_cfg["button_padding_y"],
                  sticky="e")

    root.mainloop()


if __name__ == "__main__":
    main()
