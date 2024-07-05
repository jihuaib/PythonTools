import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext

from bgp_simulator.bgp_const import BgpConst
from tools.network_tool import NetworkTool
from tools.tool_tip import Tooltip


class UdpSimulatorView:

    def __init__(self, parent):
        self.parent = parent
        self.network_utils = NetworkTool()

        # 创建一个主框架
        main_frame = tk.Frame(self.parent)
        main_frame.pack(padx=10, pady=5)

        # UDP基本参数配置部分
        udp_cfg_frame = tk.Frame(main_frame, borderwidth=2, relief=tk.SUNKEN)
        udp_cfg_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

        udp_cfg_title_frame = tk.Frame(udp_cfg_frame)
        udp_cfg_title_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(udp_cfg_title_frame, text="UDP基本参数配置").pack(side=tk.LEFT)

        udp_net_select_frame = tk.Frame(udp_cfg_frame)
        udp_net_select_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(udp_net_select_frame, text="请选择网卡： ").pack(side=tk.LEFT)
        self.interfaces = self.network_utils.get_network_interfaces()
        self.selected_interface = tk.StringVar()
        self.interface_dropdown = ttk.Combobox(udp_net_select_frame, textvariable=self.selected_interface,
                                               state="readonly", width=50)
        self.interface_dropdown['values'] = self.interfaces
        self.interface_dropdown.pack(side=tk.LEFT, padx=10)
        self.interface_dropdown.bind('<<ComboboxSelected>>', self.update_interface_info)

        udp_mac_frame = tk.Frame(udp_cfg_frame)
        udp_mac_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(udp_mac_frame, text="源MAC地址：").pack(side=tk.LEFT)
        self.entry_source_mac = tk.Entry(udp_mac_frame, width=20, state='readonly')
        self.entry_source_mac.pack(side=tk.LEFT, padx=10)

        tk.Label(udp_mac_frame, text="目的MAC地址：").pack(side=tk.LEFT)
        self.entry_dst_mac = tk.Entry(udp_mac_frame, width=20)
        self.entry_dst_mac.insert(tk.END, "00:50:56:C0:00:01")
        self.entry_dst_mac.pack(side=tk.LEFT, padx=10)

        udp_ip_frame = tk.Frame(udp_cfg_frame)
        udp_ip_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(udp_ip_frame, text="源IP地址：    ").pack(side=tk.LEFT)
        self.entry_source_ip = tk.Entry(udp_ip_frame, width=20, state='readonly')
        self.entry_source_ip.pack(side=tk.LEFT, padx=10)

        tk.Label(udp_ip_frame, text="目的IP地址：    ").pack(side=tk.LEFT)
        self.entry_dst_ip = tk.Entry(udp_ip_frame, width=20)
        self.entry_dst_ip.insert(tk.END, "192.168.56.11")
        self.entry_dst_ip.pack(side=tk.LEFT, padx=10)

        udp_port_frame = tk.Frame(udp_cfg_frame)
        udp_port_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(udp_port_frame, text="源端口：       ").pack(side=tk.LEFT)
        self.entry_source_port = tk.Entry(udp_port_frame, width=20)
        self.entry_source_port.insert(tk.END, "1234")
        self.entry_source_port.pack(side=tk.LEFT, padx=10)

        tk.Label(udp_port_frame, text="目的端口：       ").pack(side=tk.LEFT)
        self.entry_dst_port = tk.Entry(udp_port_frame, width=20)
        self.entry_dst_port.insert(tk.END, "1234")
        self.entry_dst_port.pack(side=tk.LEFT, padx=10)

        # 默认选中第一个网卡
        if self.interfaces:
            self.selected_interface.set(self.interfaces[0])
            self.update_interface_info(None)

        # 数据
        udp_data_frame = tk.Frame(main_frame, borderwidth=2, relief=tk.SUNKEN)
        udp_data_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        udp_data_title_frame = tk.Frame(udp_data_frame)
        udp_data_title_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(udp_data_title_frame, text="数据").pack(side=tk.LEFT)

        udp_data_input_frame = tk.Frame(udp_data_frame)
        udp_data_input_frame.pack(fill=tk.X, padx=10, pady=5)

        self.custom_message_text = tk.Text(udp_data_input_frame, height=10, width=50)
        self.custom_message_text.pack(fill=tk.X, padx=10, pady=5)

        udp_send_frame = tk.Frame(main_frame, borderwidth=2, relief=tk.SUNKEN)
        udp_send_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")

        udp_send_title_frame = tk.Frame(udp_send_frame)
        udp_send_title_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(udp_send_title_frame, text="发送配置").pack(side=tk.LEFT)

        # 可选参数输入框
        send_select_frame = tk.Frame(udp_send_frame)
        send_select_frame.pack(fill=tk.X, padx=10, pady=5)

        self.chk_var = tk.BooleanVar()
        chk = tk.Checkbutton(send_select_frame, text='随机生成', variable=self.chk_var,
                             command=self.auto_generate_udp_pkt_on_click)
        chk.pack(side=tk.LEFT)

        pkt_label = tk.Label(send_select_frame, text="报文长度(?)：")
        pkt_label.pack(side=tk.LEFT)
        self.entry_send_pkt_len = tk.Entry(send_select_frame, width=10)
        self.entry_send_pkt_len.pack(side=tk.LEFT)

        Tooltip(pkt_label, "（1）当输入报文长度的时候，随机生成指定长度的报文。"
                           "（2）当没输入报文长度的时候，生成的报文长度随机。")

        udp_send_para_frame = tk.Frame(udp_send_frame)
        udp_send_para_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(udp_send_para_frame, text="次数：    ").pack(side=tk.LEFT)
        self.entry_send_cnt = tk.Entry(udp_send_para_frame, width=20)
        self.entry_send_cnt.pack(side=tk.LEFT, padx=10)

        tk.Label(udp_send_para_frame, text="间隔(ms)：    ").pack(side=tk.LEFT)
        self.entry_send_interval = tk.Entry(udp_send_para_frame, width=20)
        self.entry_send_interval.pack(side=tk.LEFT, padx=10)

        send_button_frame = tk.Frame(udp_send_frame)
        send_button_frame.pack(pady=5)

        self.send_button = tk.Button(send_button_frame, text="发送")
        self.send_button.pack(side=tk.LEFT, padx=10)

        self.stop_button = tk.Button(send_button_frame, text="停止")
        self.stop_button.pack(side=tk.LEFT, padx=10)

    def auto_generate_udp_pkt_on_click(self):
        if self.chk_var.get():
            self.custom_message_text.config(state=tk.DISABLED)  # 将输入框重新设为只读
        else:
            self.custom_message_text.config(state=tk.NORMAL)

    def get_bgp_input_source_mac(self):
        return self.entry_source_mac.get().strip()

    def get_bgp_input_dst_mac(self):
        return self.entry_dst_mac.get().strip()

    def get_bgp_input_source_ip(self):
        return self.entry_source_ip.get().strip()

    def get_bgp_input_dst_ip(self):
        return self.entry_dst_ip.get().strip()

    def get_bgp_input_source_port(self):
        return self.entry_source_port.get().strip()

    def get_bgp_input_dst_port(self):
        return self.entry_dst_port.get().strip()

    def get_bgp_input_send_cnt(self):
        return self.entry_send_cnt.get().strip()

    def get_bgp_input_send_interval(self):
        return self.entry_send_interval.get().strip()

    def get_bgp_input_interface(self):
        return self.selected_interface.get()

    def update_udp_source_mac(self, mac):
        self.entry_source_mac.config(state='normal')  # 使输入框变为可写
        self.entry_source_mac.delete(0, tk.END)  # 清除输入框中的内容
        self.entry_source_mac.insert(tk.END, mac)
        self.entry_source_mac.config(state='readonly')  # 将输入框重新设为只读

    def update_udp_source_ip(self, ip):
        self.entry_source_ip.config(state='normal')  # 使输入框变为可写
        self.entry_source_ip.delete(0, tk.END)  # 清除输入框中的内容
        self.entry_source_ip.insert(tk.END, ip)
        self.entry_source_ip.config(state='readonly')  # 将输入框重新设为只读

    def update_interface_info(self, event):
        interface_name = self.selected_interface.get()
        info = self.network_utils.get_interface_info(interface_name)
        if info:
            self.update_udp_source_mac(info['MAC'])
            self.update_udp_source_ip(info['IPv4'])

    def set_controller(self, controller):
        self.send_button.config(command=controller.send_udp_on_click)
        self.stop_button.config(command=controller.stop_udp_on_click)

