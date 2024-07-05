import ipaddress
from datetime import datetime

from bgp_simulator.bgp_const import BgpConst
from tools.error_code_def import ErrCodeDef
from tools.input_validator import InputValidator, FieldValidator
from tools.messagebox_tool import show_info, show_error, show_confirm


class BgpSimulatorController:
    def __init__(self, model, view, queue):
        self.queue = queue
        self.model = model
        self.view = view
        self.view.set_controller(self)
        self.model.set_observer(self)

        self.validator = InputValidator()

    def start_bgp_on_click(self):
        if self.model.is_bgp_thread_running():
            show_info("BGP已经在运行。")
            return

        self.update_bgp_run_log('start bgp.\r\n')

        local_ip = self.view.get_bgp_input_local_ip()
        local_as = self.view.get_bgp_input_local_as()
        peer_ip = self.view.get_bgp_input_peer_ip()
        peer_as = self.view.get_bgp_input_peer_as()
        hold_time = self.view.get_bgp_input_hold_time()
        bgp_id = self.view.get_bgp_input_bgp_id()
        opt_params = self.view.get_bgp_input_opt_params()

        if not hold_time:
            hold_time = BgpConst.BGP_DEFAULT_HOLD_TIME

        if not bgp_id:
            bgp_id = local_ip

        self.validator.clear()
        self.validator.add_field('Local IP', [FieldValidator.is_not_empty, FieldValidator.is_ip_address])
        self.validator.add_field('Local AS', [FieldValidator.is_not_empty, FieldValidator.is_integer])
        self.validator.add_field('Peer IP', [FieldValidator.is_not_empty, FieldValidator.is_ip_address])
        self.validator.add_field('Peer AS', [FieldValidator.is_not_empty, FieldValidator.is_integer])
        self.validator.add_field('Hold Time', [FieldValidator.is_not_empty, FieldValidator.is_integer])
        self.validator.add_field('Router ID', [FieldValidator.is_not_empty, FieldValidator.is_ip_address])

        data = {'Local IP': local_ip,
                'Local AS': local_as,
                'Peer IP': peer_ip,
                'Peer AS': peer_as,
                'Hold Time': hold_time,
                'Router ID': bgp_id}
        if self.validator.validate(data):
            local_as = int(local_as)
            peer_as = int(peer_as)
            hold_time = int(hold_time)
            self.model.set_bgp_protocol_para(local_ip, local_as, peer_ip, peer_as, hold_time, bgp_id, opt_params)
            self.model.start_bgp_thread()
        else:
            errors = "\n".join([f"{field}: {', '.join(errs)}" for field, errs in self.validator.get_errors().items()])
            show_error(f"检验失败:\n{errors}")

    def stop_bgp_on_click(self):
        if not self.model.is_bgp_thread_running():
            show_info("BGP协议没有启动。")
            return

        self.update_bgp_run_log('stop bgp.\r\n')
        self.model.stop_bgp_thread()

    def update_bgp_run_log(self, run_log):
        now = datetime.now()
        # 格式化日期和时间
        formatted_now = now.strftime("[%Y-%m-%d %H:%M:%S]")
        self.view.update_bgp_run_log(formatted_now + run_log)

    def update_bgp_peer_state(self, peer_state):
        self.view.update_bgp_peer_state(peer_state)

    def _get_route_cfg(self, route_type):
        if route_type == 'IPv4':
            route_ip = self.view.get_route_input_ip_ipv4()
            route_mask = self.view.get_route_input_mask_ipv4()
            route_cnt = self.view.get_route_input_cnt_ipv4()
        else:
            route_ip = self.view.get_route_input_ip_ipv6()
            route_mask = self.view.get_route_input_mask_ipv6()
            route_cnt = self.view.get_route_input_cnt_ipv6()

        self.validator.clear()
        self.validator.add_field('IP', [FieldValidator.is_not_empty, FieldValidator.is_ip_address])
        self.validator.add_field('Mask', [FieldValidator.is_not_empty, FieldValidator.is_integer])
        self.validator.add_field('Count', [FieldValidator.is_not_empty, FieldValidator.is_integer])

        data = {'IP': route_ip,
                'Mask': route_mask,
                'Count': route_cnt}
        if self.validator.validate(data):
            route_mask = int(route_mask)
            route_cnt = int(route_cnt)
            return ErrCodeDef.ERROR_SUCCESS, route_ip, route_mask, route_cnt

        errors = "\n".join([f"{field}: {', '.join(errs)}" for field, errs in self.validator.get_errors().items()])
        show_error(f"检验失败:\n{errors}")
        return ErrCodeDef.ERROR_FAIL, 0, 0, 0

    @staticmethod
    def _gen_route_ips(route_type, route_ip, route_mask, route_cnt):
        ips = []
        if route_type == 'IPv4':
            network = ipaddress.ip_network(f'{route_ip}/{route_mask}', strict=False)
            for i in range(route_cnt):
                if route_mask == 32:
                    ip = network.network_address + i + 1
                else:
                    ip = network.network_address + (i * (2 ** (32 - route_mask)))
                    ip = ipaddress.ip_network(f'{ip}/{route_mask}', strict=False).network_address
                ips.append(ipaddress.ip_network(f'{ip}/{route_mask}', strict=False))
        else:
            network = ipaddress.ip_network(f'{route_ip}/{route_mask}', strict=False)
            for i in range(route_cnt):
                if route_mask == 128:
                    ip = network.network_address + i + 1
                else:
                    ip = network.network_address + (i * (2 ** (128 - route_mask)))
                    ip = ipaddress.ip_network(f'{ip}/{route_mask}', strict=False).network_address
                ips.append(ipaddress.ip_network(f'{ip}/{route_mask}', strict=False))

        return ips

    def route_send_on_click(self):
        route_type = self.view.get_route_input_type()
        ret, route_ip, route_mask, route_cnt = self._get_route_cfg(route_type)
        if ret != ErrCodeDef.ERROR_SUCCESS:
            return

        ips = self._gen_route_ips(route_type, route_ip, route_mask, route_cnt)
        self.model.route_send(route_type, ips)

    def route_cancel_on_click(self):
        route_type = self.view.get_route_input_type()
        ret, route_ip, route_mask, route_cnt = self._get_route_cfg(route_type)
        if ret != ErrCodeDef.ERROR_SUCCESS:
            return

        ips = self._gen_route_ips(route_type, route_ip, route_mask, route_cnt)
        self.model.route_withdrawn(route_type, ips)

    def on_closing(self):
        if self.model.is_bgp_thread_running():
            return show_confirm("退出", "BGP正在运行，确定要退出吗？", self.stop_bgp_on_click)
        return True

