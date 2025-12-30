#!/usr/bin/env python3
"""GitHub工具合集 - 主界面"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tkinter import ttk  # noqa: E402
from github_utils import (  # noqa: E402
    get_tools_order, get_tool_config, run_tool,
    Tooltip, AsyncTaskRunner, ResultPanel,
    create_main_window, setup_window_style, create_notebook, create_tab,
    create_button_panel, create_exit_button
)

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


def main():
    root = create_main_window()
    setup_window_style(root)
    ttk.Label(root, text=text_cfg["main_title"],
              style="Title.TLabel").pack(
                  pady=(UI_CONFIG["padding"]["title_pady_top"],
                        UI_CONFIG["padding"]["title_pady_bottom"]))

    notebook = create_notebook(root, UI_CONFIG)
    tools_frame = create_tab(notebook, UI_CONFIG["tabs"]["tools_text"],
                             UI_CONFIG["padding"]["tab_padding"])
    info_frame = create_tab(notebook, UI_CONFIG["tabs"]["info_text"],
                            UI_CONFIG["padding"]["tab_padding"])

    btn_panel = create_button_panel(tools_frame)
    btn_panel.pack(fill="x", pady=(0, 10))

    result_panel = ResultPanel(tools_frame, UI_CONFIG, layout_cfg)
    result_text = result_panel.text

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
