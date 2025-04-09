import tkinter as tk
from tkinter import ttk
import queue

from bgp_simulator.bgp_simulator_controller import BgpSimulatorController
from bgp_simulator.bgp_simulator_model import BgpSimulatorModel
from bgp_simulator.bgp_simulator_view import BgpSimulatorView
from commit.commit_controller import CommitController
from commit.commit_model import CommitModel
from commit.commit_view import CommitView
from string_generator.string_generator_model import StringGeneratorModel
from string_generator.string_generator_controller import StringGeneratorController
from string_generator.string_generator_view import StringGeneratorView
from svn.svn_controller import SvnController
from svn.svn_model import SvnModel
from svn.svn_view import SvnView
from tools.msg_def import MsgDef
from udp_simulator.udp_simulator_controller import UdpSimulatorController
from udp_simulator.udp_simulator_model import UdpSimulatorModel
from udp_simulator.udp_simulator_view import UdpSimulatorView


class ScrollableFrame(ttk.Frame):
    """带智能滚动条的容器组件"""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner_frame = ttk.Frame(self.canvas)

        # 配置画布
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        # 布局组件
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # 绑定事件
        self.inner_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # 初始隐藏滚动条
        self.scrollbar_visible = False

    def _on_frame_configure(self, event):
        """当内部框架尺寸变化时更新滚动区域"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self._check_scrollbar_needed()

    def _on_canvas_configure(self, event):
        """当画布尺寸变化时调整内部框架宽度"""
        canvas_width = event.width
        self.canvas.itemconfig("all", width=canvas_width)

    def _on_mousewheel(self, event):
        """处理鼠标滚轮事件"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _check_scrollbar_needed(self):
        """动态检查是否需要显示滚动条"""
        frame_height = self.inner_frame.winfo_height()
        canvas_height = self.canvas.winfo_height()

        if frame_height > canvas_height and not self.scrollbar_visible:
            self.scrollbar.pack(side="right", fill="y")
            self.scrollbar_visible = True
        elif frame_height <= canvas_height and self.scrollbar_visible:
            self.scrollbar.pack_forget()
            self.scrollbar_visible = False


class MainController(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("工具集合-For jihuaibin")

        self.queue = queue.Queue()
        self.tabs = {}  # 用于存储各选项卡的组件

        # style = ttk.Style()
        # style.configure("TFrame", background="#ffffff")
        # style.configure("TButton", font=("微软雅黑", 10))
        # style.configure("TLabel", font=("微软雅黑", 10))

        # 禁用最大化操作
        self.geometry("1100x800")
        self.resizable(False, False)  # 禁用窗口大小调整

        # 创建选项卡控制
        self.tab_control = ttk.Notebook(self)

        # 初始化各选项卡
        self._create_tab("字符串生成工具", StringGeneratorView)
        self._create_tab("BGP模拟工具", BgpSimulatorView)
        self._create_tab("UDP模拟工具", UdpSimulatorView)
        self._create_tab("COMMIT工具", CommitView)
        self._create_tab("SVN工具", SvnView)

        # # 创建各选项卡并添加滚动功能
        # self._create_scrolled_tab("字符串生成工具", self.tab_control)
        # self.string_generator_model = StringGeneratorModel(self.queue)
        # self.string_generator_view = StringGeneratorView(self.tabs["字符串生成工具"]["inner_frame"])
        # self.string_generator_controller = StringGeneratorController(
        #     self.string_generator_model, self.string_generator_view, self.queue)
        #
        # self._create_scrolled_tab("BGP模拟工具", self.tab_control)
        # self.bgp_simulator_model = BgpSimulatorModel(self.queue)
        # self.bgp_simulator_view = BgpSimulatorView(self.tabs["BGP模拟工具"]["inner_frame"])
        # self.bgp_simulator_controller = BgpSimulatorController(
        #     self.bgp_simulator_model, self.bgp_simulator_view, self.queue)
        #
        # self._create_scrolled_tab("UDP模拟工具", self.tab_control)
        # self.udp_simulator_model = UdpSimulatorModel(self.queue)
        # self.udp_simulator_view = UdpSimulatorView(self.tabs["UDP模拟工具"]["inner_frame"])
        # self.udp_simulator_controller = UdpSimulatorController(
        #     self.udp_simulator_model, self.udp_simulator_view, self.queue)
        #
        # self._create_scrolled_tab("COMMIT工具", self.tab_control)
        # self.commit_model = CommitModel(self.queue)
        # self.commit_view = CommitView(self.tabs["COMMIT工具"]["inner_frame"])
        # self.commit_controller = CommitController(  # 修正变量名错误
        #     self.commit_model, self.commit_view, self.queue)
        # self.commit_view.text_area.tag_config("server", foreground="blue")
        # self.commit_view.text_area.tag_config("user", foreground="green")
        # self.commit_view.text_area.tag_config("error", foreground="red")
        #
        # self._create_scrolled_tab("SVN工具", self.tab_control)
        # self.svn_model = SvnModel(self.queue)
        # self.svn_view = SvnView(self.tabs["SVN工具"]["inner_frame"])
        # self.svn_controller = SvnController(
        #     self.svn_model, self.svn_view, self.queue)

        self.tab_control.pack(expand=1, fill="both")

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self._start_queue_checker()

    def _create_tab(self, tab_name, view_class):
        """创建带滚动条的选项卡"""
        scroll_frame = ScrollableFrame(self.tab_control)
        self.tab_control.add(scroll_frame, text=tab_name)

        # 初始化视图组件
        view = view_class(scroll_frame.inner_frame)
        # view.pack(fill="both", expand=True, padx=10, pady=10)

        # 初始化MVC组件（根据具体选项卡类型）
        if tab_name == "字符串生成工具":
            self.string_generator_model = StringGeneratorModel(self.queue)
            self.string_generator_controller = StringGeneratorController(
                self.string_generator_model, view, self.queue
            )
        elif tab_name == "BGP模拟工具":
            self.bgp_simulator_model = BgpSimulatorModel(self.queue)
            self.bgp_simulator_controller = BgpSimulatorController(
                self.bgp_simulator_model, view, self.queue
            )
        elif tab_name == "UDP模拟工具":
            self.udp_simulator_model = UdpSimulatorModel(self.queue)
            self.udp_simulator_controller = UdpSimulatorController(
                self.udp_simulator_model, view, self.queue
            )
        elif tab_name == "COMMIT工具":
            self.commit_model = CommitModel(self.queue)
            self.commit_controller = CommitController(
                self.commit_model, view, self.queue
            )
        elif tab_name == "SVN工具":
            self.svn_model = SvnModel(self.queue)
            self.svn_controller = SvnController(
                self.svn_model, view, self.queue
            )

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
