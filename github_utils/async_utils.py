#!/usr/bin/env python3
"""GitHub工具合集 - 异步任务工具模块"""
import queue
import threading
from tkinter import Tk, ttk, Text, Scrollbar


class Tooltip:
    def __init__(self, widget, text, ui_config):
        self.widget = widget
        self.text = text
        self.ui_config = ui_config
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + self.ui_config["tooltip"]["offset_x"]
        y += self.widget.winfo_rooty() + self.ui_config["tooltip"]["offset_y"]

        self.tooltip_window = Tk()
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        tooltip_cfg = self.ui_config["tooltip"]
        label = ttk.Label(self.tooltip_window, text=self.text, justify="left",
                          background=tooltip_cfg["background"],
                          relief=tooltip_cfg["relief"],
                          borderwidth=tooltip_cfg["borderwidth"],
                          padding=(tooltip_cfg["padding_x"],
                                   tooltip_cfg["padding_y"]))
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


class AsyncTaskRunner:
    def __init__(self, result_callback=None):
        self.result_queue = queue.Queue()
        self.running_tasks = {}
        self.result_callback = result_callback

    def run_tool_async(self, tool_key, tool_config, run_tool_func, btn,
                       on_complete=None):
        if self.running_tasks.get(tool_key, False):
            return

        self.running_tasks[tool_key] = True
        btn.config(state="disabled")

        def task():
            try:
                result = run_tool_func(tool_config)
                self.result_queue.put((tool_key, "success", result))
            except Exception as e:
                self.result_queue.put((tool_key, "error", str(e)))

        threading.Thread(target=task, daemon=True).start()
        return self

    def check_queue(self, buttons, on_status_change=None):
        try:
            while not self.result_queue.empty():
                tool_key, status, data = self.result_queue.get_nowait()
                self.running_tasks[tool_key] = False

                for btn in buttons:
                    if btn.tool_key == tool_key:
                        btn.config(state="normal")
                        break

                if self.result_callback:
                    self.result_callback(tool_key, status, data)

                if on_status_change:
                    on_status_change(tool_key, status, data)
        except queue.Empty:
            pass

        if any(self.running_tasks.values()):
            return True
        return False


class ResultPanel:
    def __init__(self, parent, ui_config, layout_config):
        self.frame = ttk.LabelFrame(
            parent, text=ui_config["text"]["result_frame_title"],
            padding=layout_config["frame_padding"])
        self.frame.pack(fill="both", expand=True)
        self.text = Text(self.frame, wrap="word",
                         height=layout_config["result_text_height"])
        self.scrollbar = Scrollbar(self.frame, command=self.text.yview)
        self.text.config(yscrollcommand=self.scrollbar.set)
        self.text.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def insert(self, content, tag=None):
        self.text.insert("end", content + "\n", tag)
        self.text.see("end")

    def clear(self):
        self.text.delete("1.0", "end")

    def show_json(self, data):
        import json
        content = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
        self.text.insert("end", content)
        self.text.see("end")
