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
                       on_complete=None, output_func=None):
        if self.running_tasks.get(tool_key, False):
            return

        self.running_tasks[tool_key] = True
        btn.config(state="disabled")

        def task():
            try:
                result = run_tool_func(tool_config, output_func)
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
        self.progress_line_num = None
        self._active_progress = False

    def insert(self, content, tag=None):
        self.text.insert("end", content + "\n", tag)
        self.text.see("end")

    def clear(self):
        self.text.delete("1.0", "end")
        self.progress_line_num = None
        self._active_progress = False

    def show_json(self, data):
        import json
        content = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
        self.text.insert("end", content)
        self.text.see("end")

    def create_progress_output_func(self):
        """创建进度条输出函数，适用于UI显示"""
        if self._active_progress:
            return None
        
        self._active_progress = True
        
        def output_func(line):
            line = line.strip()
            if not line:
                return
            
            current_line_count = int(self.text.index("end-1c").split('.')[0])
            
            if self.progress_line_num is None or self.progress_line_num > current_line_count:
                self.text.insert("end", line + "\n")
                self.progress_line_num = current_line_count
            else:
                start_idx = f"{self.progress_line_num}.0"
                end_idx = f"{self.progress_line_num + 1}.0"
                try:
                    self.text.delete(start_idx, end_idx)
                except Exception:
                    pass
                self.text.insert(start_idx, line + "\n")
            self.text.see("end")
        return output_func

    def clear_progress(self):
        """清除进度条状态并清理相关文本"""
        if self.progress_line_num is not None:
            try:
                line_count = int(self.text.index("end-1c").split('.')[0])
                if self.progress_line_num <= line_count:
                    start_idx = f"{self.progress_line_num}.0"
                    end_idx = f"{self.progress_line_num + 1}.0"
                    self.text.delete(start_idx, end_idx)
                else:
                    self._find_and_clear_progress()
            except Exception:
                self._find_and_clear_progress()
        self.progress_line_num = None
        self._active_progress = False

    def _find_and_clear_progress(self):
        """查找并清理包含进度条内容的行"""
        try:
            content = self.text.get("1.0", "end")
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'Working...' in line or '[|]' in line or '[/]' in line or '[-]' in line or '[\\]' in line:
                    start_idx = f"{i + 1}.0"
                    end_idx = f"{i + 2}.0"
                    self.text.delete(start_idx, end_idx)
                    break
        except Exception:
            pass

    def clear_all_progress(self):
        """清理所有可能存在的进度条行（用于强制清理）"""
        content = self.text.get("1.0", "end")
        lines = content.split('\n')
        progress_patterns = ['Working...', '[|]', '[/]', '[-]', '[\\]']
        
        for i, line in enumerate(lines):
            if any(p in line for p in progress_patterns):
                try:
                    start_idx = f"{i + 1}.0"
                    end_idx = f"{i + 2}.0"
                    self.text.delete(start_idx, end_idx)
                except Exception:
                    pass
        
        self.progress_line_num = None
        self._active_progress = False
