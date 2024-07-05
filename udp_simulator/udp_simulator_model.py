import threading
import time

from tools.network_tool import NetworkTool


class UdpSimulatorModel:
    def __init__(self, queue):
        self._controller = None
        self._lock = threading.Lock()

        self.queue = queue

        self._interface = None
        self._source_mac = None
        self._dst_mac = None
        self._source_ip = None
        self._dst_ip = None
        self._source_port = None
        self._dst_port = None
        self._send_cnt = None
        self._send_interval = None

        self.udp_thread = None
        self.running_lock = threading.Lock()
        self.running = False

        self.share_data_lock = threading.Lock()
        self.share_data = None

    def set_udp_para(self, interface ,source_mac, dst_mac, source_ip, dst_ip, source_port, dst_port, send_cnt,
                     send_interval):
        self._interface = interface
        self._source_mac = source_mac
        self._dst_mac = dst_mac
        self._source_ip = source_ip
        self._dst_ip = dst_ip
        self._source_port = source_port
        self._dst_port = dst_port
        self._send_cnt = send_cnt
        self._send_interval = send_interval

    def set_observer(self, observer):
        self._controller = observer

    def start_udp_thread(self):
        if not self.is_udp_thread_running():
            self.udp_thread = threading.Thread(target=self._start_udp)
            self.udp_thread.start()
            while not self.is_udp_thread_running():  # 等待子线程启动
                time.sleep(0.1)

    def set_udp_thread_running(self, value):
        with self.running_lock:
            self.running = value

    def is_udp_thread_running(self):
        with self.running_lock:
            return self.running

    def set_udp_share_data(self, value):
        with self.share_data_lock:
            self.share_data = value

    def get_udp_share_data(self):
        with self.share_data_lock:
            return self.share_data

    def stop_udp_thread(self):
        if self.udp_thread.is_alive():  # 检查子线程是否在运行
            self.udp_thread.join()

    def _start_udp(self):
        self.set_udp_thread_running(True)  # 标记子线程已启动
        NetworkTool.send_custom_udp(self._interface, self._source_mac, self._dst_mac, self._source_ip, self._dst_ip,
                                    self._source_port, self._dst_port, '')
        self.set_udp_thread_running(False)
