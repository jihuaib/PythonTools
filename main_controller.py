import tkinter as tk
from tkinter import ttk
import queue
import platform
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

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.inner_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        self.scrollbar_visible = False
        # 绑定鼠标滚轮事件（不同系统）
        self._bind_mousewheel()

    def _bind_mousewheel(self):
        """智能绑定鼠标滚轮事件"""

        def on_mousewheel(event):
            # 判断事件来源组件是否支持滚动
            widget = event.widget
            if isinstance(widget, (tk.Text, tk.Listbox, ttk.Treeview)):
                # 检查是否还能继续滚动
                first, last = widget.yview()
                if (event.delta < 0 or event.num == 5) and last < 1.0:
                    return  # 允许组件自行处理
                elif (event.delta > 0 or event.num == 4) and first > 0.0:
                    return  # 允许组件自行处理

            # 触发外层滚动
            if platform.system() == "Windows":
                self._on_mousewheel_windows(event)
            elif platform.system() == "Darwin":
                self._on_mousewheel_mac(event)
            else:
                if event.num == 4:
                    self._on_mousewheel_linux_up(event)
                elif event.num == 5:
                    self._on_mousewheel_linux_down(event)

        # 绑定到所有子组件
        self.inner_frame.bind_all("<MouseWheel>", on_mousewheel)
        self.inner_frame.bind_all("<Button-4>", on_mousewheel)
        self.inner_frame.bind_all("<Button-5>", on_mousewheel)

        # 动态绑定新添加的组件
        self.inner_frame.bind("<Map>", lambda e: self._bind_child_mousewheel())

    def _bind_child_mousewheel(self):
        """为所有子组件绑定滚动事件"""

        def bind_recursive(widget):
            for child in widget.winfo_children():
                child.bind("<MouseWheel>", self._pass_mousewheel)
                child.bind("<Button-4>", self._pass_mousewheel)
                child.bind("<Button-5>", self._pass_mousewheel)
                bind_recursive(child)

        bind_recursive(self.inner_frame)

    def _pass_mousewheel(self, event):
        os_name = platform.system()
        if os_name == "Windows":
            self.canvas.event_generate("<MouseWheel>", delta=event.delta)
        elif os_name == "Darwin":
            self.canvas.event_generate("<MouseWheel>", delta=event.delta)
        else:
            if event.num == 4:
                self.canvas.event_generate("<Button-4>")
            elif event.num == 5:
                self.canvas.event_generate("<Button-5>")
        return "break"

    def _bind_linux_mousewheel(self):
        self.canvas.bind_all("<Button-4>", self._on_mousewheel_linux_up)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel_linux_down)

    def _unbind_linux_mousewheel(self):
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_mousewheel_windows(self, event):
        self.canvas.yview_scroll(-1 * int(event.delta / 120), "units")

    def _on_mousewheel_mac(self, event):
        self.canvas.yview_scroll(-1 * int(event.delta), "units")

    def _on_mousewheel_linux_up(self, event):
        self.canvas.yview_scroll(-1, "units")

    def _on_mousewheel_linux_down(self, event):
        self.canvas.yview_scroll(1, "units")

    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self._check_scrollbar_needed()

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _check_scrollbar_needed(self):
        frame_height = self.inner_frame.winfo_height()
        canvas_height = self.canvas.winfo_height()

        if frame_height > canvas_height and not self.scrollbar_visible:
            self.scrollbar.pack(side="right", fill="y")
            self.scrollbar_visible = True
        elif frame_height <= canvas_height and self.scrollbar_visible:
            self.scrollbar.pack_forget()
            self.scrollbar_visible = False

    def disable_mousewheel(self):
        """禁用外层滚动条对鼠标滚轮的响应"""
        os_name = platform.system()
        if os_name == "Windows":
            self.canvas.unbind_all("<MouseWheel>")
        elif os_name == "Darwin":
            self.canvas.unbind_all("<MouseWheel>")
        else:
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")

    def enable_mousewheel(self):
        """重新启用外层滚动条鼠标滚轮响应"""
        self._bind_mousewheel()  # 就是你原来绑定滚轮事件的函数


class MainController(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("工具集合-For jihuaibin")

        self.queue = queue.Queue()
        self.tabs = {}  # 用于存储各选项卡的组件

        # 禁用最大化操作
        self.geometry("1100x900")
        self.resizable(False, False)  # 禁用窗口大小调整

        # 创建选项卡控制
        self.tab_control = ttk.Notebook(self)

        # 初始化各选项卡
        self._create_tab("字符串生成工具", StringGeneratorView)
        self._create_tab("BGP模拟工具", BgpSimulatorView)
        self._create_tab("UDP模拟工具", UdpSimulatorView)
        self._create_tab("COMMIT工具", CommitView)
        self._create_tab("SVN工具", SvnView)

        self.tab_control.pack(expand=1, fill="both")

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self._start_queue_checker()

    def _create_tab(self, tab_name, view_class):
        """创建带滚动条的选项卡"""
        scroll_frame = ScrollableFrame(self.tab_control)
        self.tab_control.add(scroll_frame, text=tab_name)

        # 初始化视图组件并正确布局
        view = view_class(scroll_frame.inner_frame)
        view.pack(fill="both", expand=True, padx=10, pady=10)  # 必须添加这行布局代码

        # 强制更新布局计算
        self.update_idletasks()
        scroll_frame._check_scrollbar_needed()

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
