import telnetlib
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext


class CommitView:

    def __init__(self, parent):
        self.parent = parent

        # 创建一个主框架
        main_frame = tk.Frame(self.parent)
        main_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        # Address and Port Entry
        self.address_label = tk.Label(main_frame, text="Server Address:")
        self.address_label.pack()
        self.address_entry = tk.Entry(main_frame)
        self.address_entry.insert(tk.END, "192.168.56.11")
        self.address_entry.pack()

        self.port_label = tk.Label(main_frame, text="Port:")
        self.port_label.pack()
        self.port_entry = tk.Entry(main_frame)
        self.port_entry.insert(tk.END, "23")
        self.port_entry.pack()

        # Connect Button
        self.connect_button = tk.Button(main_frame, text="Connect", command=self.connect_telnet)
        self.connect_button.pack()

        # Text area to display output
        self.text_area = scrolledtext.ScrolledText(main_frame, width=80, height=20, wrap=tk.WORD)
        self.text_area.pack(fill=tk.BOTH, expand=True)

        # Configure tags for different text types
        self.text_area.tag_config("server", foreground="blue")
        self.text_area.tag_config("user", foreground="green")
        self.text_area.tag_config("error", foreground="red")

        self.input_start_mark = "input_start"

        # self.text_area.bind("<Tab>", self.handle_tab)
        # self.text_area.bind("<Return>", self.handle_enter)
        # self.text_area.bind("<Key>", self.prevent_modification)
        self.text_area.bind("<KeyRelease>", self.process_input)

        # Telnet connection object
        self.telnet_connection = None
        self.connected = False

    def connect_telnet(self):
        self.server = self.address_entry.get()
        self.port = int(self.port_entry.get())
        try:
            self.telnet_connection = telnetlib.Telnet(self.server, self.port)
            self.connected = True
            self.append_text(f"Connected to {self.server} on port {self.port}\r\n", "server")
            # Start a thread to continuously read from the Telnet connection
            threading.Thread(target=self.read_from_telnet, daemon=True).start()
        except Exception as e:
            self.append_text(f"Failed to connect: {e}\r\n", "error")

    def read_from_telnet(self):
        while self.connected:
            try:
                output = self.telnet_connection.read_very_eager().decode('ascii')
                if output:
                    self.append_text(output, "server")
            except EOFError:
                self.append_text("Connection closed by the remote host.\r\n", "server")
                self.connected = False
                break

    # def handle_enter(self, event=None):
    #     # Handle Enter key
    #     self.process_input()
    #     return "break"  # Prevent default behavior of adding a newline
    #
    # def handle_tab(self, event=None):
    #     # Handle Tab key
    #     self.process_input()
    #     return "break"  # Prevent default Tab behavior

    def process_input(self, event):
        print(f"Key pressed: {event.keysym} (Key code: {event.keycode})")
        if self.connected:
            # 删除已输入的文本
            self.text_area.delete(self.input_start_mark, tk.END)
            # 重置 input_start_mark 标记到原位置
            self.text_area.mark_set(self.input_start_mark, self.input_start_index)
            user_input = self.text_area.get(self.input_start_mark, tk.END).strip()
            print('input ' + user_input)

            self.telnet_connection.write(user_input.encode('ascii'))

    def prevent_modification(self, event):
        # 只允许修改输入区域后的内容
        if self.text_area.compare("insert", "<", self.input_start_mark):
            return "break"

    def append_text(self, text, tag):
        # Insert text and apply the appropriate tag
        self.text_area.insert(tk.END, text)
        self.text_area.tag_add(tag, "end-1c linestart", "end-1c")
        self.text_area.see(tk.END)

        # 重新设置 input_start 标记为服务器返回数据的结束处
        self.text_area.mark_set(self.input_start_mark, "end-1c")
        self.input_start_index = self.text_area.index(self.input_start_mark)

    def set_controller(self, controller):
        pass
