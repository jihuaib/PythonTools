import tkinter as tk
from tkinter import messagebox, scrolledtext


class StringGeneratorView:

    def __init__(self, parent):
        self.parent = parent

        # 创建一个主框架
        main_frame = tk.Frame(self.parent)
        main_frame.pack(padx=10, pady=5)

        self.str_cfg_frame = tk.Frame(main_frame, borderwidth=2, relief=tk.SUNKEN)
        self.str_cfg_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

        str_cfg_title_frame = tk.Frame(self.str_cfg_frame)
        str_cfg_title_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(str_cfg_title_frame, text="参数配置").pack(side=tk.LEFT)

        str_template_frame = tk.Frame(self.str_cfg_frame)
        str_template_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(str_template_frame, text="模板：").pack(side=tk.LEFT)
        self.text_template = scrolledtext.ScrolledText(str_template_frame, wrap=tk.WORD, height=10, width=50)
        self.text_template.insert(tk.END, "ip addr 1.1.{A}.1 24")
        self.text_template.pack(side=tk.LEFT, padx=10)

        str_para_frame_1 = tk.Frame(self.str_cfg_frame)
        str_para_frame_1.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(str_para_frame_1, text="占位符：").pack(side=tk.LEFT)
        self.entry_placeholder_1 = tk.Entry(str_para_frame_1, width=5)
        self.entry_placeholder_1.insert(tk.END, "A")
        self.entry_placeholder_1.pack(side=tk.LEFT, padx=10)

        tk.Label(str_para_frame_1, text="起始值：").pack(side=tk.LEFT)
        self.entry_start_1 = tk.Entry(str_para_frame_1, width=5)
        self.entry_start_1.insert(tk.END, "1")
        self.entry_start_1.pack(side=tk.LEFT, padx=10)

        tk.Label(str_para_frame_1, text="结束值：").pack(side=tk.LEFT)
        self.entry_end_1 = tk.Entry(str_para_frame_1, width=5)
        self.entry_end_1.insert(tk.END, "2")
        self.entry_end_1.pack(side=tk.LEFT, padx=10)

        str_btn_frame = tk.Frame(self.str_cfg_frame)
        str_btn_frame.pack(pady=10)

        self.generate_button = tk.Button(str_btn_frame, text="生成")
        self.generate_button.pack(side=tk.LEFT, padx=10)

        str_gen_text_title_frame = tk.Frame(self.str_cfg_frame)
        str_gen_text_title_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(str_gen_text_title_frame, text="结果").pack(side=tk.LEFT)

        self.str_gen_text_frame = tk.Frame(self.str_cfg_frame)
        self.str_gen_text_frame.pack(fill=tk.X, padx=10, pady=5)

        self.text_output = scrolledtext.ScrolledText(self.str_gen_text_frame, wrap=tk.WORD, width=60, height=15)
        self.text_output.pack(fill=tk.BOTH, expand=True)
        self.text_output.config(state=tk.DISABLED)  # 初始设置为不可编辑状态

        # 添加右键菜单
        self.text_output.bind("<Button-3>", self.popup_menu)

    def set_controller(self, controller):
        self.generate_button.config(command=controller.generate_strings_on_click)

    def popup_menu(self, event):
        popup = tk.Menu(self.str_gen_text_frame, tearoff=0)
        popup.add_command(label="全选", command=self.select_all)
        popup.add_command(label="复制", command=self.copy_to_clipboard)
        popup.add_command(label="清空", command=self.clear_output)
        popup.tk_popup(event.x_root, event.y_root)

    def select_all(self):
        self.text_output.tag_add("sel", "1.0", tk.END)

    def copy_to_clipboard(self):
        try:
            selected_text = self.text_output.selection_get()
            self.str_gen_text_frame.clipboard_clear()
            self.str_gen_text_frame.clipboard_append(selected_text)
        except tk.TclError:
            messagebox.showerror("错误", "没有选中文本可以复制。")

    def clear_output(self):
        self.text_output.config(state=tk.NORMAL)
        self.text_output.delete("1.0", tk.END)
        self.text_output.config(state=tk.DISABLED)

    def get_input_template(self):
        return self.text_template.get("1.0", tk.END).strip()

    def get_input_para1(self):
        entry_placeholder = self.entry_placeholder_1.get().strip()
        entry_start = self.entry_start_1.get().strip()
        entry_end = self.entry_end_1.get().strip()

        return entry_placeholder, entry_start, entry_end

    def update_gen_text_output(self, strings):
        # 显示生成的字符串列表
        strings_output = "\n".join(strings)
        self.text_output.config(state=tk.NORMAL)
        self.text_output.delete("1.0", tk.END)
        self.text_output.insert(tk.END, strings_output + "\n")
        self.text_output.config(state=tk.DISABLED)
