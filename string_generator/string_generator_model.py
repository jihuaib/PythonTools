from tools.msg_def import MsgDef


class StringGeneratorModel:
    def __init__(self, queue):
        self._controller = None
        self.queue = queue

    def set_observer(self, observer):
        self._controller = observer

    def generate_strings(self, template, placeholder_1, start_value_1, end_value_1):
        strings_1 = []

        start_value_1 = int(start_value_1)
        end_value_1 = int(end_value_1)
        for value in range(start_value_1, end_value_1 + 1):
            current_template = template.replace("{" + placeholder_1 + "}", str(value))
            strings_1.append(current_template)

        self.queue.put((MsgDef.MSG_STRING_GENERATOR, strings_1))
