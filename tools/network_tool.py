import wmi
from scapy.layers.inet import IP, UDP
from scapy.layers.l2 import Ether
from scapy.sendrecv import sendp


class NetworkTool:
    def __init__(self):
        self.wmi_obj = wmi.WMI()

    def get_network_interfaces(self):
        interfaces = []
        for nic in self.wmi_obj.Win32_NetworkAdapterConfiguration(IPEnabled=True):
            interfaces.append(nic.Description)
        return interfaces

    def get_interface_info(self, interface_description):
        for nic in self.wmi_obj.Win32_NetworkAdapterConfiguration(IPEnabled=True):
            if nic.Description == interface_description:
                result = {
                    'IPv4': [],
                    'IPv6': [],
                    'MAC': nic.MACAddress
                }
                if nic.IPAddress:
                    for ip in nic.IPAddress:
                        if ':' in ip:
                            result['IPv6'].append(ip)
                        else:
                            result['IPv4'].append(ip)
                return result
        return None

    @staticmethod
    def send_custom_udp(interface, src_mac, dst_mac, src_ip, dst_ip, src_port, dst_port, message):
        # 创建以太网帧，指定源和目标MAC地址
        ether = Ether(src=src_mac, dst=dst_mac)
        # 创建IP数据包
        ip = IP(src=src_ip, dst=dst_ip)
        # 创建UDP数据包
        udp = UDP(sport=src_port, dport=dst_port)
        # 将消息添加到UDP数据包
        data = message.encode('utf-8')
        # 构建完整的数据包
        packet = ether / ip / udp / data
        # 发送数据包
        sendp(packet, interface)
