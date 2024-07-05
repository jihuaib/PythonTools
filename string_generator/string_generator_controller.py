import threading

from tools.input_validator import InputValidator, FieldValidator
from tools.messagebox_tool import show_error


class StringGeneratorController:
    def __init__(self, model, view, queue):
        self.queue = queue
        self.model = model
        self.view = view
        self.view.set_controller(self)
        self.model.set_observer(self)

        self.validator = InputValidator()

    def _validate_input_para(self, placeholder,  start_value, end_value):
        if not placeholder:
            return True

        self.validator.clear()
        self.validator.add_field('占位符', [FieldValidator.is_not_empty])
        self.validator.add_field('起始值', [FieldValidator.is_not_empty, FieldValidator.is_integer])
        self.validator.add_field('结束值', [FieldValidator.is_not_empty, FieldValidator.is_integer])

        data = {'占位符': placeholder,
                '起始值': start_value,
                '结束值': end_value}
        if self.validator.validate(data):
            self.validator.validate_relationship(
                data,
                "起始值", "结束值",
                lambda x, y: x <= y,
                "起始值必须小于结束值。"
            )

        if self.validator.get_errors():
            errors = "\n".join([f"{field}: {', '.join(errs)}" for field, errs in self.validator.get_errors().items()])
            show_error(f"检验失败:\n{errors}")
            return False

        return True

    def generate_strings_on_click(self):
        self.validator.clear()
        # 获取用户输入的模板
        template = self.view.get_input_template()
        self.validator.add_field('字符串模板', [FieldValidator.is_not_empty])

        # 获取占位符和其范围
        placeholder_1,  start_value_1, end_value_1 = self.view.get_input_para1()

        data = {'字符串模板': template}

        if self.validator.validate(data):
            if self._validate_input_para(placeholder_1, start_value_1, end_value_1):
                threading.Thread(target=self.model.generate_strings,
                                 args=(template,placeholder_1, start_value_1, end_value_1)).start()
        else:
            errors = "\n".join([f"{field}: {', '.join(errs)}" for field, errs in self.validator.get_errors().items()])
            show_error(f"检验失败:\n{errors}")

    def update_gen_text_output(self, strings):
        self.view.update_gen_text_output(strings)