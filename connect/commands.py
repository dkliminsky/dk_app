from .connect import DKConnect
from .utils import bytes_to_uint, int32_to_bytes, int16_to_bytes


class DKCommands:
    DEVICE_NAME = None

    def __init__(self, connect: DKConnect):
        self.connect = connect

    def device_name(self) -> str:
        return self.DEVICE_NAME


class DKGeneralCommands(DKCommands):
    COMMAND_ECHO = 0
    COMMAND_GET_NAME = 1
    COMMAND_GET_UID = 2
    COMMAND_GET_SOFTWARE_VERSION = 3
    COMMAND_SYSTEM_RESET = 4

    def ping(self) -> bool:
        data = self.connect.exchange(self.COMMAND_ECHO, b'ping')
        return data == b'ping'

    def get_name(self) -> str:
        data = self.connect.exchange(self.COMMAND_GET_NAME, None)
        return data.decode('latin-1')

    def get_uid(self) -> bytes:
        data = self.connect.exchange(self.COMMAND_GET_UID, None)
        return data

    def get_software_version(self) -> (int, int, int, int):
        data = self.connect.exchange(self.COMMAND_GET_SOFTWARE_VERSION, None)
        return data[0], data[1], bytes_to_uint(data[2:4])

    def system_reset(self):
        self.connect.send(self.COMMAND_SYSTEM_RESET, None)
        self.connect.disconnect()

