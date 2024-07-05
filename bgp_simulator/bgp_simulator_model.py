import ipaddress
import select
import socket
import struct
import threading
import time

from bgp_simulator.bgp_const import BgpConst
from tools.messagebox_tool import show_error
from tools.msg_def import MsgDef


class BgpSimulatorModel:
    def __init__(self, queue):
        self._controller = None
        self._lock = threading.Lock()

        self.queue = queue

        # bgp参数
        self._opt_params = None
        self._bgp_id = None
        self._hold_time = None
        self._peer_as = None
        self._peer_ip = None
        self._local_as = None
        self._local_ip = None

        self.server_socket = None
        self.client_socket = None
        self.udp_sock = None

        self.marker = b'\xff' * 16  # 16字节全F
        self.version = 4  # BGP版本号

        self.peer_state = BgpConst.BGP_PEER_STATE_NONE

        self.bgp_thread = None
        self.running_lock = threading.Lock()
        self.running = False

        self.share_data_lock = threading.Lock()
        self.share_data = None

    def set_bgp_protocol_para(self, local_ip, local_as, peer_ip, peer_as, hold_time, bgp_id, opt_params):
        self._local_ip = local_ip
        self._local_as = local_as
        self._peer_ip = peer_ip
        self._peer_as = peer_as
        self._hold_time = hold_time
        self._bgp_id = bgp_id
        self._opt_params = opt_params

    def set_observer(self, observer):
        self._controller = observer

    def ntfy_main_bgp_run_log(self, run_log):
        self.queue.put((MsgDef.MSG_BGP_RUN_LOG, run_log))

    def ntfy_main_change_peer_state(self, peer_state):
        self.queue.put((MsgDef.MSG_BGP_PEER_STATE, peer_state))

    def start_bgp_thread(self):
        if not self.is_bgp_thread_running():
            self.bgp_thread = threading.Thread(target=self._start_bgp)
            self.bgp_thread.start()
            while not self.is_bgp_thread_running():  # 等待子线程启动
                time.sleep(0.1)

    def _send_message(self, message):
        # 发送消息到子线程
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        address = self.udp_sock.getsockname()
        s.sendto(message, address)
        s.close()

    def set_bgp_thread_running(self, value):
        with self.running_lock:
            self.running = value

    def is_bgp_thread_running(self):
        with self.running_lock:
            return self.running

    def set_share_data(self, value):
        with self.share_data_lock:
            self.share_data = value

    def get_share_data(self):
        with self.share_data_lock:
            return self.share_data

    def stop_bgp_thread(self):
        if self.bgp_thread.is_alive():  # 检查子线程是否在运行
            self._send_message(b'stop')
            self.bgp_thread.join()

    def _start_bgp(self):
        self.set_bgp_thread_running(True)  # 标记子线程已启动
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((self._local_ip, 179))
            self.server_socket.listen(1)

            self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp_sock.bind((self._local_ip, 12345))

            self.ntfy_main_bgp_run_log(f'listen {self._local_ip}:179.\r\n')
            self.change_peer_state(BgpConst.BGP_PEER_STATE_IDLE)
        except OSError:
            self.ntfy_main_bgp_run_log(f"port listen fail.\r\n")
            self.set_bgp_thread_running(False)
            if self.udp_sock is not None:
                self.udp_sock.close()
                self.udp_sock = None
            if self.server_socket is not None:
                self.server_socket.close()
                self.server_socket = None
            self.ntfy_main_bgp_run_log(f"Server has stopped.\r\n")
            return

        sockets_to_read = [self.server_socket, self.udp_sock]

        try:
            while self.is_bgp_thread_running():
                readable, _, _ = select.select(sockets_to_read, [], [], 0.1)
                for sock in readable:
                    if sock == self.server_socket:
                        if self.client_socket is not None:
                            self.ntfy_main_bgp_run_log(f'存在bgp链接，不允许建立新的bgp链接.\r\n')
                        else:
                            self.client_socket, client_address = self.server_socket.accept()
                            self.ntfy_main_bgp_run_log(f'Accepted connection from {client_address}.\r\n')
                            self.client_socket.setblocking(False)
                            sockets_to_read.append(self.client_socket)
                            self.change_peer_state(BgpConst.BGP_PEER_STATE_CONNECT)
                            self.send_bgp_open_msg()
                            self.change_peer_state(BgpConst.BGP_PEER_STATE_OPEN_SENT)
                    elif sock == self.client_socket:
                        header = sock.recv(BgpConst.BGP_HEAD_LEN)
                        if not header:
                            # 关闭连接
                            self.client_socket.close()
                            sockets_to_read.remove(self.client_socket)
                            self.client_socket = None
                            break

                        if not self.handle_bgp_packet(header):
                            self.client_socket.close()
                            sockets_to_read.remove(self.client_socket)
                            self.client_socket = None
                            break
                    elif sock == self.udp_sock:
                        data, _ = self.udp_sock.recvfrom(1024)
                        if data.startswith(b'stop'):
                            self.set_bgp_thread_running(False)
                            self.change_peer_state(BgpConst.BGP_PEER_STATE_IDLE)
                            break
                        else:
                            self._process_udp_message(data)
        except OSError as e:
            self.ntfy_main_bgp_run_log(f"Error occurred: {e}.\r\n")
        finally:
            self.set_bgp_thread_running(False)
            if self.udp_sock is not None:
                self.udp_sock.close()
                self.udp_sock = None
            if self.client_socket is not None:
                self.client_socket.close()
                self.client_socket = None
            if self.server_socket is not None:
                self.server_socket.close()
                self.server_socket = None
            self.ntfy_main_bgp_run_log(f"Server has stopped.\r\n")

    def _process_udp_message(self, data):
        if data.startswith(b'send_route_ipv4'):
            self.send_bgp_route(self.share_data)
        elif data.startswith(b'withdrawn_route_ipv4'):
            self.withdrawn_bgp_route(self.share_data)
        elif data.startswith(b'send_route_ipv6'):
            self.send_bgp_route_ipv6(self.share_data)
        elif data.startswith(b'withdrawn_route_ipv6'):
            self.withdrawn_bgp_route_ipv6(self.share_data)
        else:
            self.ntfy_main_bgp_run_log(f"Received unknown message: {data}.\r\n")

    def change_peer_state(self, peer_state):
        if self.peer_state == peer_state:
            return

        self.ntfy_main_bgp_run_log(f'bgp fsm state {BgpConst.BGP_PEER_STATE[self.peer_state]} ->'
                                   f'{BgpConst.BGP_PEER_STATE[peer_state]}.\r\n')
        self.peer_state = peer_state
        self.ntfy_main_change_peer_state(BgpConst.BGP_PEER_STATE[peer_state])

    def create_bgp_open_opt_params(self):
        opt_params = b''
        for opt in self._opt_params:
            if opt == BgpConst.BGP_OPEN_OPT_CAP_IPV4UNC:
                opt_params += struct.pack('!BBBBBBBB', 0x02, 0x06, 0x01, 0x04, 0x00, 0x01, 0x00, 0x01)
            elif opt == BgpConst.BGP_OPEN_OPT_CAP_ROUTE_REFRESH:
                opt_params += struct.pack('!BBBB', 0x02, 0x02, 0x02, 0x00)
            elif opt == BgpConst.BGP_OPEN_OPT_CAP_AS4:
                opt_params += struct.pack('!BBBBI', 0x02, 0x06, 0x41, 0x04, self._local_as)
            if opt == BgpConst.BGP_OPEN_OPT_CAP_IPV6UNC:
                opt_params += struct.pack('!BBBBBBBB', 0x02, 0x06, 0x01, 0x04, 0x00, 0x02, 0x00, 0x01)
        return opt_params

    def create_bgp_open_msg(self):
        # 创建BGP OPEN消息
        opt_params = self.create_bgp_open_opt_params()
        opt_param_len = len(opt_params)

        bgp_id_ip_network = ipaddress.ip_network(self._bgp_id)
        prefix_bytes = bgp_id_ip_network.network_address.packed

        # BGP OPEN消息的固定头部和OPEN消息内容（10字节）
        bgp_open_header = struct.pack('!BHH', self.version, self._local_as,
                                      self._hold_time) + prefix_bytes + struct.pack('!B', opt_param_len)

        # BGP消息的整体格式（含16字节marker）
        length = 29 + opt_param_len  # BGP OPEN消息的总长度（含16字节marker + 3字节固定头部 + 10字节OPEN消息 + 可选参数）
        msg_type = BgpConst.BGP_OPEN  # 消息类型（OPEN）

        # BGP消息的整体格式（含16字节marker）
        bgp_message = struct.pack('!16sHB', self.marker, length, msg_type) + bgp_open_header + opt_params

        return bgp_message

    def create_bgp_keepalive_msg(self):
        # BGP消息的整体格式（含16字节marker）
        length = BgpConst.BGP_HEAD_LEN  # KEEPALIVE消息的总长度（含16字节marker + 3字节固定头部）
        msg_type = BgpConst.BGP_KEEPALIVE  # 消息类型（OPEN）

        bgp_message = struct.pack('!16sHB', self.marker, length, msg_type)

        return bgp_message

    def _create_path_attributes(self):
        origin = struct.pack('!BBBB', 0x40, 0x01, 0x01, 0x00)  # ORIGIN
        as_path = struct.pack('!BBBBBI', 0x40, 0x02, 0x06, 0x02, 0x01, self._local_as)  # AS_PATH
        next_hop = struct.pack('!BBB4s', 0x40, 0x03, 0x04, ipaddress.ip_address(self._local_ip).packed)  # NEXT_HOP

        return origin + as_path + next_hop

    def _create_path_attributes_ipv6(self, route):
        origin = struct.pack('!BBBB', 0x40, 0x01, 0x01, 0x00)  # ORIGIN
        as_path = struct.pack('!BBBBBI', 0x40, 0x02, 0x06, 0x02, 0x01, self._local_as)  # AS_PATH
        med = struct.pack('!BBBI', 0x80, 0x04, 0x04, 0x0)  # MED

        ipv4_nexthop = ipaddress.ip_address(self._local_ip)
        ipv6_mapped = ipaddress.IPv6Address('::ffff:' + str(ipv4_nexthop))

        ip_network = ipaddress.ip_network(route)
        packed_ip = ip_network.network_address.packed
        # MP_REACH_NLRI
        mp_reach_nlri = struct.pack('!BBHHBB16sH16s', 0x90, 0x0E, 0x26, 0x02, 0x01, len(ipv6_mapped.packed),
                                    ipv6_mapped.packed, ip_network.prefixlen, packed_ip)
        return origin + as_path + med + mp_reach_nlri

    def _create_nlri(self, route):
        ip_network = ipaddress.ip_network(route)
        prefix_length = ip_network.prefixlen
        prefix_bytes = ip_network.network_address.packed
        nlri = struct.pack('!B', prefix_length) + prefix_bytes

        return nlri

    def create_withdrawn_update_msg(self, route):
        network = ipaddress.ip_network(route)
        prefix_length = network.prefixlen
        prefix_bytes = network.network_address.packed

        withdrawn_routes = struct.pack('!B', prefix_length) + prefix_bytes
        path_attributes = struct.pack('!H', 0)
        update_msg = struct.pack('!H', len(withdrawn_routes)) + withdrawn_routes + path_attributes

        msg_len = BgpConst.BGP_HEAD_LEN + len(update_msg)
        msg_type = BgpConst.BGP_UPDATE
        header = struct.pack('!16sHB', self.marker, msg_len, msg_type)

        full_update_msg = header + update_msg
        return full_update_msg

    def create_withdrawn_update_msg_ipv6(self, route):
        withdrawn_routes_length = 0

        ip_network = ipaddress.ip_network(route)
        packed_ip = ip_network.network_address.packed

        # MP_UN_REACH_NLRI
        mp_un_reach_nlri = struct.pack('!BBHHBB16s', 0x90, 0x0F, 0x14, 0x02, 0x01,
                                       ip_network.prefixlen, packed_ip)

        # BGP UPDATE message
        update_msg = struct.pack('!H', withdrawn_routes_length)
        update_msg += struct.pack('!H', len(mp_un_reach_nlri)) + mp_un_reach_nlri

        # BGP message header
        msg_length = BgpConst.BGP_HEAD_LEN + len(update_msg)
        msg_type = BgpConst.BGP_UPDATE
        msg_header = struct.pack('!16sHB', self.marker, msg_length, msg_type)

        return msg_header + update_msg

    def create_bgp_update_msg(self, route):
        # Withdrawn Routes Length
        withdrawn_routes_length = 0

        # Path Attributes
        path_attributes = self._create_path_attributes()

        # Network Layer Reachability Information (NLRI)
        nlri = self._create_nlri(route)

        # Total Path Attribute Length
        total_path_attribute_length = len(path_attributes)

        # BGP UPDATE message
        update_msg = struct.pack('!H', withdrawn_routes_length)
        update_msg += struct.pack('!H', total_path_attribute_length) + path_attributes + nlri

        # BGP message header
        msg_length = BgpConst.BGP_HEAD_LEN + len(update_msg)
        msg_type = BgpConst.BGP_UPDATE
        msg_header = struct.pack('!16sHB', self.marker, msg_length, msg_type)

        return msg_header + update_msg

    def create_bgp_update_msg_ipv6(self, route):
        # Withdrawn Routes Length
        withdrawn_routes_length = 0

        # Path Attributes
        path_attributes = self._create_path_attributes_ipv6(route)

        # BGP UPDATE message
        update_msg = struct.pack('!H', withdrawn_routes_length)
        update_msg += struct.pack('!H',  len(path_attributes)) + path_attributes

        # BGP message header
        msg_length = BgpConst.BGP_HEAD_LEN + len(update_msg)
        msg_type = BgpConst.BGP_UPDATE
        msg_header = struct.pack('!16sHB', self.marker, msg_length, msg_type)

        return msg_header + update_msg

    def create_bgp_notification_msg(self):
        length = BgpConst.BGP_HEAD_LEN
        msg_type = BgpConst.BGP_KEEPALIVE  # 消息类型（OPEN）

        bgp_message = struct.pack('!16sHB', self.marker, length, msg_type)

        return bgp_message

    def send_bgp_open_msg(self):
        # 发送BGP OPEN消息
        bgp_open_msg = self.create_bgp_open_msg()
        self.client_socket.sendall(bgp_open_msg)

    def send_bgp_keepalive_msg(self):
        bgp_msg = self.create_bgp_keepalive_msg()
        self.client_socket.sendall(bgp_msg)

    def handle_bgp_packet(self, header):
        marker, length, msg_type = struct.unpack("!16sHB", header)

        if length > BgpConst.BGP_HEAD_LEN:
            msg = self.client_socket.recv(length - BgpConst.BGP_HEAD_LEN)
            if not msg:
                return False
            data = header + msg
        else:
            data = header

        if msg_type == BgpConst.BGP_OPEN:
            self.ntfy_main_bgp_run_log(f'recv bgp open pkt.\r\n')
            self.handle_open_message()
            self.change_peer_state(BgpConst.BGP_PEER_STATE_OPEN_CONFIRM)
        elif msg_type == BgpConst.BGP_KEEPALIVE:
            self.ntfy_main_bgp_run_log(f'recv bgp keepalive pkt.\r\n')
            self.change_peer_state(BgpConst.BGP_PEER_STATE_ESTABLISH)
            self.send_bgp_keepalive_msg()
        elif msg_type == BgpConst.BGP_NOTIFICATION:
            self.ntfy_main_bgp_run_log(f'recv bgp notification pkt.\r\n')
            self.change_peer_state(BgpConst.BGP_PEER_STATE_IDLE)
            self.client_socket.close()
            return False
        return True

    def handle_open_message(self):
        self.send_bgp_keepalive_msg()

    def withdrawn_bgp_route(self, ips):
        update_msgs = [self.create_withdrawn_update_msg(route) for route in ips]

        # 使用一个队列存储待发送的消息
        pending_msgs = update_msgs.copy()

        self.ntfy_main_bgp_run_log(f'begin withdrawn ipv4 route:{len(ips)}.\r\n')

        while pending_msgs:
            try:
                # 从队列中取出第一个待发送的消息
                update_msg = pending_msgs[0]
                sent = self.client_socket.send(update_msg)
                # 如果消息部分发送，更新消息内容
                if sent < len(update_msg):
                    pending_msgs[0] = update_msg[sent:]
                else:
                    pending_msgs.pop(0)  # 完整发送后移除消息
            except BlockingIOError:
                # 使用select等待套接字变为可写
                select.select([], [self.client_socket], [])

        self.ntfy_main_bgp_run_log(f'end withdrawn ipv4 route:{len(ips)}.\r\n')

    def withdrawn_bgp_route_ipv6(self, ips):
        update_msgs = [self.create_withdrawn_update_msg_ipv6(route) for route in ips]

        # 使用一个队列存储待发送的消息
        pending_msgs = update_msgs.copy()

        self.ntfy_main_bgp_run_log(f'begin withdrawn ipv6 route:{len(ips)}.\r\n')

        while pending_msgs:
            try:
                # 从队列中取出第一个待发送的消息
                update_msg = pending_msgs[0]
                sent = self.client_socket.send(update_msg)
                # 如果消息部分发送，更新消息内容
                if sent < len(update_msg):
                    pending_msgs[0] = update_msg[sent:]
                else:
                    pending_msgs.pop(0)  # 完整发送后移除消息
            except BlockingIOError:
                # 使用select等待套接字变为可写
                select.select([], [self.client_socket], [])

        self.ntfy_main_bgp_run_log(f'end withdrawn ipv6 route:{len(ips)}.\r\n')

    def route_send(self, route_type, ips):
        if self.peer_state != BgpConst.BGP_PEER_STATE_ESTABLISH:
            show_error("BGP邻居状态需要为ESTABLISH状态。")
            return
        self.set_share_data(ips)
        if route_type == 'IPv4':
            self._send_message(b'send_route_ipv4')
        else:
            self._send_message(b'send_route_ipv6')

    def route_withdrawn(self, route_type, ips):
        if self.peer_state != BgpConst.BGP_PEER_STATE_ESTABLISH:
            show_error("BGP邻居状态需要为ESTABLISH状态。")
            return
        self.set_share_data(ips)
        if route_type == 'IPv4':
            self._send_message(b'withdrawn_route_ipv4')
        else:
            self._send_message(b'withdrawn_route_ipv6')

    def send_bgp_route(self, ips):
        update_msgs = [self.create_bgp_update_msg(route) for route in ips]

        # 使用一个队列存储待发送的消息
        pending_msgs = update_msgs.copy()

        self.ntfy_main_bgp_run_log(f'begin send ipv4 route:{len(ips)}.\r\n')

        while pending_msgs:
            try:
                # 从队列中取出第一个待发送的消息
                update_msg = pending_msgs[0]
                sent = self.client_socket.send(update_msg)
                # 如果消息部分发送，更新消息内容
                if sent < len(update_msg):
                    pending_msgs[0] = update_msg[sent:]
                else:
                    pending_msgs.pop(0)  # 完整发送后移除消息
            except BlockingIOError:
                # 使用select等待套接字变为可写
                select.select([], [self.client_socket], [])

        self.ntfy_main_bgp_run_log(f'end send ipv4 route:{len(ips)}.\r\n')

    def send_bgp_route_ipv6(self, ips):
        update_msgs = [self.create_bgp_update_msg_ipv6(route) for route in ips]

        # 使用一个队列存储待发送的消息
        pending_msgs = update_msgs.copy()

        self.ntfy_main_bgp_run_log(f'begin send ipv6 route:{len(ips)}.\r\n')

        while pending_msgs:
            try:
                # 从队列中取出第一个待发送的消息
                update_msg = pending_msgs[0]
                sent = self.client_socket.send(update_msg)
                # 如果消息部分发送，更新消息内容
                if sent < len(update_msg):
                    pending_msgs[0] = update_msg[sent:]
                else:
                    pending_msgs.pop(0)  # 完整发送后移除消息
            except BlockingIOError:
                # 使用select等待套接字变为可写
                select.select([], [self.client_socket], [])

        self.ntfy_main_bgp_run_log(f'end send ipv6 route:{len(ips)}.\r\n')
