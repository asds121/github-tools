#!/usr/bin/env python3
"""GitHub工具合集 - GUI构建工具模块"""
from tkinter import Tk, ttk
from .common_utils import get_ui_config


def create_main_window(title=None, size=None):
    """创建主窗口"""
    ui_config = get_ui_config()
    window_cfg = ui_config["window"]

    root = Tk()
    root.title(title or window_cfg["title"])
    root.geometry(size or window_cfg["size"])
    return root


def setup_window_style(root, style_config=None):
    """设置窗口样式"""
    ui_config = get_ui_config()
    style = ttk.Style()
    style_config = style_config or ui_config["style"]
    style.configure("Title.TLabel", font=tuple(style_config["title_font"]))
    return style


def create_notebook(parent, ui_config=None):
    """创建选项卡控件"""
    ui_config = ui_config or get_ui_config()
    notebook = ttk.Notebook(parent)
    pady = (ui_config["padding"]["root_pady_top"],
            ui_config["padding"]["root_pady_bottom"])
    notebook.pack(fill="both", expand=True,
                  padx=ui_config["padding"]["root_padx"], pady=pady)
    return notebook


def create_tab(notebook, name, padding=None, ui_config=None):
    """创建选项卡"""
    ui_config = ui_config or get_ui_config()
    frame = ttk.Frame(notebook,
                      padding=padding or ui_config["padding"]["tab_padding"])
    notebook.add(frame, text=name)
    return frame


def create_button_panel(parent, ui_config=None):
    """创建按钮面板"""
    return ttk.Frame(parent)


def create_exit_button(parent, command, ui_config=None):
    """创建退出按钮"""
    ui_config = ui_config or get_ui_config()
    layout_cfg = ui_config["layout"]
    btn = ttk.Button(parent, text="退出", command=command,
                     width=layout_cfg["exit_button_width"])
    return btn


class ToolButton(ttk.Button):
    def __init__(self, parent, tool_key, tool_config, command, layout_config):
        self.tool_key = tool_key
        super().__init__(parent, text=tool_config["name"],
                         command=lambda: command(tool_key, self),
                         width=layout_config["tool_button_width"])
