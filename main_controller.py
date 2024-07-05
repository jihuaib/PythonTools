import tkinter as tk
from tkinter import ttk
import queue

from bgp_simulator.bgp_simulator_controller import BgpSimulatorController
from bgp_simulator.bgp_simulator_model import BgpSimulatorModel
from bgp_simulator.bgp_simulator_view import BgpSimulatorView
from string_generator.string_generator_model import StringGeneratorModel
from string_generator.string_generator_controller import StringGeneratorController
from string_generator.string_generator_view import StringGeneratorView
from tools.msg_def import MsgDef
from udp_simulator.udp_simulator_controller import UdpSimulatorController
from udp_simulator.udp_simulator_model import UdpSimulatorModel
from udp_simulator.udp_simulator_view import UdpSimulatorView


class MainController(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("工具集合-For jihuaibin")

        self.queue = queue.Queue()

        # 创建选项卡控制
        self.tab_control = ttk.Notebook(self)

        # 创建字符串生成工具的选项卡
        self.string_generator_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.string_generator_tab, text="字符串生成工具")

        self.string_generator_model = StringGeneratorModel(self.queue)
        self.string_generator_view = StringGeneratorView(self.string_generator_tab)
        self.string_generator_controller = StringGeneratorController(self.string_generator_model,
                                                                     self.string_generator_view,
                                                                     self.queue)

        # 创建BGP模拟工具的选项卡
        self.bgp_simulator_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.bgp_simulator_tab, text="BGP模拟工具")

        self.bgp_simulator_model = BgpSimulatorModel(self.queue)
        self.bgp_simulator_view = BgpSimulatorView(self.bgp_simulator_tab)
        self.bgp_simulator_controller = BgpSimulatorController(self.bgp_simulator_model,
                                                               self.bgp_simulator_view,
                                                               self.queue)
        # 创建UDP模拟工具的选项卡
        self.udp_simulator_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.udp_simulator_tab, text="UDP模拟工具")

        self.udp_simulator_model = UdpSimulatorModel(self.queue)
        self.udp_simulator_view = UdpSimulatorView(self.udp_simulator_tab)
        self.udp_simulator_controller = UdpSimulatorController(self.udp_simulator_model,
                                                               self.udp_simulator_view,
                                                               self.queue)
        self.tab_control.pack(expand=1, fill="both")

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self._start_queue_checker()

    def on_closing(self):
        if self.bgp_simulator_controller.on_closing():
            self.destroy()

    def _start_queue_checker(self):
        self._check_queue()

    def _check_queue(self):
        try:
            msg = self.queue.get_nowait()
            msg_type, text = msg
            if msg_type == MsgDef.MSG_STRING_GENERATOR:
                self.string_generator_controller.update_gen_text_output(text)
            elif msg_type == MsgDef.MSG_BGP_RUN_LOG:
                self.bgp_simulator_controller.update_bgp_run_log(text)
            elif msg_type == MsgDef.MSG_BGP_PEER_STATE:
                self.bgp_simulator_controller.update_bgp_peer_state(text)
        except queue.Empty:
            pass
        finally:
            self.tab_control.after(100, self._check_queue)


if __name__ == "__main__":
    app = MainController()
    app.mainloop()
