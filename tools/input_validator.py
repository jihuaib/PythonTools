import ipaddress
import re


class FieldValidator:
    @staticmethod
    def is_not_empty(value):
        if not value:
            return "值不能为空。"

    @staticmethod
    def is_integer(value):
        try:
            int(value)
        except ValueError:
            return "值必须为整数。"

    @staticmethod
    def is_ip_address(value):
        try:
            ipaddress.ip_address(value)
        except ValueError:
            return "值必须为IP地址。"

    @staticmethod
    def matches_regex(value, pattern, error_message="Value does not match the required pattern."):
        if not re.match(pattern, value):
            return error_message

    @staticmethod
    def compare_values(value1, value2, comparison, error_message):
        try:
            val1 = float(value1)
            val2 = float(value2)
            if not comparison(val1, val2):
                return error_message
        except ValueError:
            return "Values must be numbers for comparison."


class InputValidator:
    def __init__(self):
        self.fields = {}
        self.errors = {}

    def add_field(self, field_name, validators):
        self.fields[field_name] = validators

    def clear(self):
        self.fields = {}
        self.errors = {}

    def validate(self, data):
        self.errors = {}
        for field, validators in self.fields.items():
            value = data.get(field, "")
            for validator in validators:
                if isinstance(validator, tuple):
                    result = validator[0](value, *validator[1:])
                else:
                    result = validator(value)
                if result:
                    if field not in self.errors:
                        self.errors[field] = []
                    self.errors[field].append(result)
        return len(self.errors) == 0

    def validate_relationship(self, data, field1, field2, comparison, error_message):
        value1 = data.get(field1, "")
        value2 = data.get(field2, "")
        result = FieldValidator.compare_values(value1, value2, comparison, error_message)
        if result:
            if field1 not in self.errors:
                self.errors[field1] = []
            self.errors[field1].append(result)

    def get_errors(self):
        return self.errors
