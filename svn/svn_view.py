import telnetlib
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog, ttk


class SvnView(ttk.Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        # 创建一个主框架
        main_frame = tk.Frame(self.parent)
        main_frame.pack(padx=10, pady=5)

        # BGP配置部分
        svn_switch_frame = tk.Frame(main_frame, borderwidth=2, relief=tk.SUNKEN)
        svn_switch_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

        svn_switch_title_frame = tk.Frame(svn_switch_frame)
        svn_switch_title_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(svn_switch_title_frame, text="SVN批量切换").pack(side=tk.LEFT)

        svn_switch_input_frame = tk.Frame(svn_switch_frame)
        svn_switch_input_frame.pack(fill=tk.X, padx=10, pady=5)

        button = tk.Button(svn_switch_input_frame, text="选择目录", command=self.select_directory)
        button.pack(side=tk.LEFT, padx=10)

        tk.Label(svn_switch_input_frame, text="切换目的URL：").pack(side=tk.LEFT)
        self.svn_switch_dst_url = tk.Entry(svn_switch_input_frame, width=25)
        self.svn_switch_dst_url.pack(side=tk.LEFT, padx=10)

        svn_switch_button_frame = tk.Frame(svn_switch_frame)
        svn_switch_button_frame.pack(pady=5)

        self.svn_switch_button = tk.Button(svn_switch_button_frame, text="切换")
        self.svn_switch_button.pack(side=tk.LEFT, padx=10)

        log_frame = tk.Frame(svn_switch_frame)
        log_frame.pack(fill=tk.X, padx=10, pady=5)

        self.text_output = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, width=60, height=15)
        self.text_output.pack(fill=tk.BOTH, expand=True)
        self.text_output.config(state=tk.DISABLED)  # 初始设置为不可编辑状态

    def select_directory(self):
        # 打开目录选择对话框
        directory = filedialog.askdirectory()
        if directory:
            # 如果选择了目录，则打印路径
            print(f"选择的目录: {directory}")

    def set_controller(self, controller):
        pass
