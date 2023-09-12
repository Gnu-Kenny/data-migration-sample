from enum import Enum


class StatusType(Enum):
    def __init__(self, code):
        self.code = code

    READY = "READY"
    RUNNING = "RUN"
    TERMINATED = "DONE"

    UNKNOWN = ""

    @staticmethod
    def get_type(code):
        return type_map.get(code, StatusType.UNKNOWN)

    def equals(self, code: str):
        return StatusType[self.name] == self.get_type(code)


type_map = {}
for type_instance in StatusType:
    type_map[type_instance.code] = type_instance
