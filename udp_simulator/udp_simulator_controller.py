from scapy.sendrecv import sniff

from tools.input_validator import InputValidator, FieldValidator
from tools.messagebox_tool import show_info


class UdpSimulatorController:
    def __init__(self, model, view, queue):
        self.queue = queue
        self.model = model
        self.view = view
        self.view.set_controller(self)
        self.model.set_observer(self)

        self.validator = InputValidator()

    @staticmethod
    def check_winpcap_installed():
        try:
            # 示例：尝试嗅探一个数据包来检查是否安装了 WinPcap 或 Npcap
            sniff(count=1)
            return True
        except RuntimeError as e:
            if "winpcap is not installed" in str(e).lower():
                return False
            else:
                show_info(e)
                return False

    def send_udp_on_click(self):
        if not self.check_winpcap_installed():
            show_info('winpcap is not installed')
            return

        source_mac = self.view.get_bgp_input_source_mac()
        dst_mac = self.view.get_bgp_input_dst_mac()
        source_ip = self.view.get_bgp_input_source_ip()
        dst_ip = self.view.get_bgp_input_dst_ip()
        source_port = self.view.get_bgp_input_source_port()
        dst_port = self.view.get_bgp_input_dst_port()
        interface = self.view.get_bgp_input_interface()

        source_port = int(source_port)
        dst_port = int(dst_port)

        send_cnt = self.view.get_bgp_input_send_cnt()
        send_interval = self.view.get_bgp_input_send_interval()

        self.model.set_udp_para(interface, source_mac, dst_mac, source_ip, dst_ip, source_port, dst_port, send_cnt,
                                send_interval)

        self.model.start_udp_thread()

    def stop_udp_on_click(self):
        if not self.check_winpcap_installed():
            show_info('winpcap is not installed')
            return
        self.model.stop_udp_thread()
