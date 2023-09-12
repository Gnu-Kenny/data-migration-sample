from enum import Enum


class ResultType(Enum):
    def __init__(self, code):
        self.code = code

    FAIL = "FAIL"
    SUCCESS = "SUCCESS"

    UNKNOWN = ""

    @staticmethod
    def get_type(code):
        return type_map.get(code, ResultType.UNKNOWN)

    def equals(self, code: str):
        return ResultType[self.name] == self.get_type(code)


type_map = {}
for type_instance in ResultType:
    type_map[type_instance.code] = type_instance
