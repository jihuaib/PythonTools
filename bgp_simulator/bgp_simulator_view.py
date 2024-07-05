import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext

from bgp_simulator.bgp_const import BgpConst
from tools.network_tool import NetworkTool


class BgpSimulatorView:

    def __init__(self, parent):
        self.parent = parent
        self.network_utils = NetworkTool()

        self.optional_params_vars = {
            BgpConst.BGP_OPEN_OPT_CAP_IPV4UNC: tk.IntVar(value=1),
            BgpConst.BGP_OPEN_OPT_CAP_ROUTE_REFRESH: tk.IntVar(value=1),
            BgpConst.BGP_OPEN_OPT_CAP_AS4: tk.IntVar(value=1),
            BgpConst.BGP_OPEN_OPT_CAP_IPV6UNC: tk.IntVar(value=0)
        }
        # 创建一个主框架
        main_frame = tk.Frame(self.parent)
        main_frame.pack(padx=10, pady=5)

        # BGP配置部分
        bgp_cfg_frame = tk.Frame(main_frame, borderwidth=2, relief=tk.SUNKEN)
        bgp_cfg_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

        bgp_cfg_title_frame = tk.Frame(bgp_cfg_frame)
        bgp_cfg_title_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(bgp_cfg_title_frame, text="BGP配置").pack(side=tk.LEFT)

        bgp_net_select_frame = tk.Frame(bgp_cfg_frame)
        bgp_net_select_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(bgp_net_select_frame, text="请选择网卡：").pack(side=tk.LEFT)
        self.interfaces = self.network_utils.get_network_interfaces()

        self.selected_interface = tk.StringVar()
        self.interface_dropdown = ttk.Combobox(bgp_net_select_frame, textvariable=self.selected_interface,
                                               state="readonly", width=50)
        self.interface_dropdown['values'] = self.interfaces
        self.interface_dropdown.pack(side=tk.LEFT, padx=10)
        self.interface_dropdown.bind('<<ComboboxSelected>>', self.update_interface_info)

        # 本地AS号输入
        local_frame = tk.Frame(bgp_cfg_frame)
        local_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(local_frame, text="Local IP：   ").pack(side=tk.LEFT)
        self.entry_local_ip = tk.Entry(local_frame, width=20, state='readonly')
        self.entry_local_ip.pack(side=tk.LEFT, padx=10)

        # 默认选中第一个网卡
        if self.interfaces:
            self.selected_interface.set(self.interfaces[0])
            self.update_interface_info(None)

        tk.Label(local_frame, text="Local AS：").pack(side=tk.LEFT)
        self.entry_local_as = tk.Entry(local_frame, width=20)
        self.entry_local_as.insert(tk.END, "65535")
        self.entry_local_as.pack(side=tk.LEFT, padx=10)

        # BGP邻居信息输入
        peer_frame = tk.Frame(bgp_cfg_frame)
        peer_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(peer_frame, text="Peer IP：    ").pack(side=tk.LEFT)
        self.entry_peer_ip = tk.Entry(peer_frame, width=20)
        self.entry_peer_ip.insert(tk.END, "192.168.56.11")
        self.entry_peer_ip.pack(side=tk.LEFT, padx=10)

        tk.Label(peer_frame, text="Peer AS： ").pack(side=tk.LEFT)
        self.entry_peer_as = tk.Entry(peer_frame, width=20)
        self.entry_peer_as.insert(tk.END, "100")
        self.entry_peer_as.pack(side=tk.LEFT, padx=10)

        # BGP路由器ID输入框
        bgp_id_frame = tk.Frame(bgp_cfg_frame)
        bgp_id_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(bgp_id_frame, text="Router ID： ").pack(side=tk.LEFT)
        self.bgp_id_entry = tk.Entry(bgp_id_frame, width=20)
        self.bgp_id_entry.pack(side=tk.LEFT, padx=10)

        # 持续时间输入框
        hold_time_frame = tk.Frame(bgp_cfg_frame)
        hold_time_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(hold_time_frame, text="Hold Time：").pack(side=tk.LEFT)
        self.hold_time_entry = tk.Entry(hold_time_frame, width=20)
        self.hold_time_entry.pack(side=tk.LEFT, padx=10)

        # 可选参数输入框
        optional_params_frame = tk.Frame(bgp_cfg_frame)
        optional_params_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(optional_params_frame, text="Optional Param：").pack(side=tk.LEFT)
        for option, var in self.optional_params_vars.items():
            chk = tk.Checkbutton(optional_params_frame, text=option, variable=var)
            chk.pack(side=tk.LEFT, padx=10)

        # BGP Peer状态显示
        peer_state_frame = tk.Frame(bgp_cfg_frame)
        peer_state_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(peer_state_frame, text="Peer State：").pack(side=tk.LEFT)

        self.entry_peer_state_var = tk.StringVar(value="")
        self.entry_peer_state = tk.Entry(peer_state_frame, width=20, textvariable=self.entry_peer_state_var,
                                         state='readonly')
        self.entry_peer_state.pack(side=tk.LEFT, padx=10)

        bgp_button_frame = tk.Frame(bgp_cfg_frame)
        bgp_button_frame.pack(pady=5)

        self.start_bgp_button = tk.Button(bgp_button_frame, text="Start", )
        self.start_bgp_button.pack(side=tk.LEFT, padx=10)

        self.stop_bgp_button = tk.Button(bgp_button_frame, text="Stop", )
        self.stop_bgp_button.pack(side=tk.LEFT, padx=10)

        # 日志文本框
        bgp_log_frame = tk.Frame(main_frame, borderwidth=2, relief=tk.SUNKEN)
        bgp_log_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=5, sticky="nsew")

        self.bgp_log_text = scrolledtext.ScrolledText(bgp_log_frame, wrap=tk.WORD, width=60, height=20)
        self.bgp_log_text.pack(fill=tk.BOTH, expand=True)

        # Route配置部分
        route_cfg_frame = tk.Frame(main_frame, borderwidth=2, relief=tk.SUNKEN)
        route_cfg_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        route_cfg_title_frame = tk.Frame(route_cfg_frame)
        route_cfg_title_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(route_cfg_title_frame, text="Route配置").pack(side=tk.LEFT)

        self.ip_version = tk.StringVar(value="IPv4")
        ipv4_button = tk.Radiobutton(route_cfg_title_frame, text="IPv4", variable=self.ip_version, value="IPv4", command=self.switch_frame)
        ipv6_button = tk.Radiobutton(route_cfg_title_frame, text="IPv6", variable=self.ip_version, value="IPv6", command=self.switch_frame)
        ipv4_button.pack(side=tk.LEFT, padx=10)
        ipv6_button.pack(side=tk.LEFT, padx=10)

        self.config_container = tk.Frame(route_cfg_frame)
        self.config_container.pack(fill=tk.X, padx=10, pady=5)

        # Route configuration frame for IPv4
        self.route_cfg_frame_ipv4 = tk.Frame(self.config_container, borderwidth=2, relief=tk.SUNKEN)
        self.route_cfg_frame_ipv4.pack(fill=tk.X, padx=10, pady=5)

        route_frame_ipv4 = tk.Frame(self.route_cfg_frame_ipv4)
        route_frame_ipv4.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(route_frame_ipv4, text="IP：").pack(side=tk.LEFT)
        self.entry_route_ip_ipv4 = tk.Entry(route_frame_ipv4, width=25)
        self.entry_route_ip_ipv4.insert(tk.END, "1.1.1.0")
        self.entry_route_ip_ipv4.pack(side=tk.LEFT, padx=10)

        tk.Label(route_frame_ipv4, text="Mask：").pack(side=tk.LEFT)
        self.entry_route_mask_ipv4 = tk.Entry(route_frame_ipv4, width=10)
        self.entry_route_mask_ipv4.insert(tk.END, "24")
        self.entry_route_mask_ipv4.pack(side=tk.LEFT, padx=10)

        tk.Label(route_frame_ipv4, text="Count：").pack(side=tk.LEFT)
        self.entry_route_count_ipv4 = tk.Entry(route_frame_ipv4, width=10)
        self.entry_route_count_ipv4.insert(tk.END, "24")
        self.entry_route_count_ipv4.pack(side=tk.LEFT, padx=10)

        # Route configuration frame for IPv6
        self.route_cfg_frame_ipv6 = tk.Frame(self.config_container, borderwidth=2, relief=tk.SUNKEN)
        self.route_cfg_frame_ipv6.pack(fill=tk.X, padx=10, pady=5)
        self.route_cfg_frame_ipv6.pack_forget()

        route_frame_ipv6 = tk.Frame(self.route_cfg_frame_ipv6)
        route_frame_ipv6.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(route_frame_ipv6, text="IP：").pack(side=tk.LEFT)
        self.entry_route_ip_ipv6 = tk.Entry(route_frame_ipv6, width=25)
        self.entry_route_ip_ipv6.insert(tk.END, "2001:0db8::")
        self.entry_route_ip_ipv6.pack(side=tk.LEFT, padx=10)

        tk.Label(route_frame_ipv6, text="Mask：").pack(side=tk.LEFT)
        self.entry_route_mask_ipv6 = tk.Entry(route_frame_ipv6, width=10)
        self.entry_route_mask_ipv6.insert(tk.END, "64")
        self.entry_route_mask_ipv6.pack(side=tk.LEFT, padx=10)

        tk.Label(route_frame_ipv6, text="Count：").pack(side=tk.LEFT)
        self.entry_route_count_ipv6 = tk.Entry(route_frame_ipv6, width=10)
        self.entry_route_count_ipv6.insert(tk.END, "24")
        self.entry_route_count_ipv6.pack(side=tk.LEFT, padx=10)

        route_button_frame = tk.Frame(route_cfg_frame)
        route_button_frame.pack(pady=5)

        self.route_send_button = tk.Button(route_button_frame, text="发送")
        self.route_send_button.pack(side=tk.LEFT, padx=10)

        self.route_cancel_button = tk.Button(route_button_frame, text="撤销")
        self.route_cancel_button.pack(side=tk.LEFT, padx=10)

        self.route_cfg_frame_ipv4.pack(fill=tk.X, padx=10, pady=5)

    def switch_frame(self):
        if self.ip_version.get() == "IPv4":
            self.route_cfg_frame_ipv6.pack_forget()
            self.route_cfg_frame_ipv4.pack(fill=tk.X, padx=10, pady=5)
        else:
            self.route_cfg_frame_ipv4.pack_forget()
            self.route_cfg_frame_ipv6.pack(fill=tk.X, padx=10, pady=5)

    def set_controller(self, controller):
        self.start_bgp_button.config(command=controller.start_bgp_on_click)
        self.stop_bgp_button.config(command=controller.stop_bgp_on_click)
        self.route_send_button.config(command=controller.route_send_on_click)
        self.route_cancel_button.config(command=controller.route_cancel_on_click)

    def get_bgp_input_local_ip(self):
        return self.entry_local_ip.get().strip()

    def get_bgp_input_local_as(self):
        return self.entry_local_as.get().strip()

    def get_bgp_input_peer_ip(self):
        return self.entry_peer_ip.get().strip()

    def get_bgp_input_peer_as(self):
        return self.entry_peer_as.get().strip()

    def get_bgp_input_bgp_id(self):
        return self.bgp_id_entry.get().strip()

    def get_bgp_input_hold_time(self):
        return self.hold_time_entry.get().strip()

    def get_bgp_input_opt_params(self):
        opt_params = [key for key, var in self.optional_params_vars.items() if var.get() == 1]
        return opt_params

    def get_route_input_type(self):
        return self.ip_version.get()

    def get_route_input_ip_ipv4(self):
        return self.entry_route_ip_ipv4.get().strip()

    def get_route_input_mask_ipv4(self):
        return self.entry_route_mask_ipv4.get().strip()

    def get_route_input_cnt_ipv4(self):
        return self.entry_route_count_ipv4.get().strip()

    def get_route_input_ip_ipv6(self):
        return self.entry_route_ip_ipv6.get().strip()

    def get_route_input_mask_ipv6(self):
        return self.entry_route_mask_ipv6.get().strip()

    def get_route_input_cnt_ipv6(self):
        return self.entry_route_count_ipv6.get().strip()

    def update_bgp_run_log(self, log):
        self.bgp_log_text.insert(tk.END, log)
        self.bgp_log_text.see(tk.END)

    def update_bgp_peer_state(self, peer_state):
        self.entry_peer_state.config(state='normal')  # 使输入框变为可写
        self.entry_peer_state_var.set(peer_state)  # 更新输入框内容
        self.entry_peer_state.config(state='readonly')  # 将输入框重新设为只读

    def update_bgp_local_ip(self, local_ip):
        self.entry_local_ip.config(state='normal')  # 使输入框变为可写
        self.entry_local_ip.delete(0, tk.END)  # 清除输入框中的内容
        self.entry_local_ip.insert(tk.END, local_ip)
        self.entry_local_ip.config(state='readonly')  # 将输入框重新设为只读

    def update_interface_info(self, event):
        interface_name = self.selected_interface.get()
        info = self.network_utils.get_interface_info(interface_name)
        if info:
            self.update_bgp_local_ip(info['IPv4'])
