import os
from typing import Union

from .commands import DKGeneralCommands
from .utils import bytes_to_float, bytes_to_uint, int16_to_bytes, int32_to_bytes, float_to_bytes, int8_to_bytes


class SoundInfo:

    def get_id(self):
        return self._id

    def __init__(self, _id, size, pos, model_id=0, version_major=0, version_minor=0):
        self._id = _id
        self.size = size
        self.pos = pos
        self.model_id = model_id
        self.version_major = version_major
        self.version_minor = version_minor

    @staticmethod
    def unpack(data: bytes):
        return SoundInfo(
            bytes_to_uint(data[0:2]),
            bytes_to_uint(data[2:6]),
            bytes_to_uint(data[6:10]),
            bytes_to_uint(data[10:2]),
            bytes_to_uint(data[12:13]),
            bytes_to_uint(data[13:14]),
            )


class DKTankCommands(DKGeneralCommands):
    DEVICE_NAME = 'DK Tank'

    # Get info
    COMMAND_GET_HARDWARE_VERSION = 10
    COMMAND_GET_LICENSE_KEY = 11
    COMMAND_GET_ACCESS_LEVEL = 12
    COMMAND_GET_FREE_MEM = 13
    COMMAND_GET_VOLTAGE_BATTERY = 14
    COMMAND_GET_VOLTAGE_5V = 15

    COMMAND_GET_PLAYER_PERFORMANCE = 20

    COMMAND_GET_PARAM = 30
    COMMAND_SET_PARAM = 31
    COMMAND_SAVE_PARAMS = 32
    COMMAND_RESET_PARAMS = 33

    COMMAND_WRITE_LICENSE_KEY = 101

    COMMAND_WRITE_SOUND_INFO = 110
    COMMAND_WRITE_SOUND_FILE = 111
    COMMAND_GET_SOUND_INFO = 112
    COMMAND_RESET_SOUNDS = 113

    COMMAND_WRITE_HARDWARE_VERSION = 150
    COMMAND_READ_FLASH = 151
    COMMAND_START_TESTS = 152

    def get_hardware_version(self) -> (int, int, int, int):
        data = self.connect.exchange(self.COMMAND_GET_HARDWARE_VERSION, None)
        return data[0], data[1], bytes_to_uint(data[2:4])

    def get_license_key(self) -> bytes:
        data = self.connect.exchange(self.COMMAND_GET_LICENSE_KEY, None)
        return data

    def get_access_level(self) -> int:
        data = self.connect.exchange(self.COMMAND_GET_ACCESS_LEVEL, None)
        return bytes_to_uint(data)

    def get_free_mem(self) -> int:
        data = self.connect.exchange(self.COMMAND_GET_FREE_MEM, None)
        return bytes_to_uint(data)

    def get_voltage_battery(self) -> float:
        data = self.connect.exchange(self.COMMAND_GET_VOLTAGE_BATTERY, None)
        return bytes_to_float(data)

    def get_voltage_5v(self) -> float:
        data = self.connect.exchange(self.COMMAND_GET_VOLTAGE_5V, None)
        return bytes_to_float(data)

    def get_player_performance(self):
        data = self.connect.exchange(self.COMMAND_GET_PLAYER_PERFORMANCE, None)
        return bytes_to_uint(data)

    def get_param(self, number: int) -> Union[int, float]:
        params = int16_to_bytes(number)
        data = self.connect.exchange(self.COMMAND_GET_PARAM, params)
        if len(data) == 4:
            return bytes_to_float(data)
        elif len(data) == 2:
            return bytes_to_uint(data)
        else:
            return data[0]

    def set_param(self, number: int, value: Union[int, float, bool]):
        params = int16_to_bytes(number)
        if isinstance(value, int):
            params += int16_to_bytes(value)
        elif isinstance(value, float):
            params += float_to_bytes(value)
        elif isinstance(value, bool):
            params += int16_to_bytes(int(value))

        self.connect.exchange(self.COMMAND_SET_PARAM, params)

    def save_params(self):
        self.connect.exchange(self.COMMAND_SAVE_PARAMS)

    def reset_params(self):
        self.connect.exchange(self.COMMAND_RESET_PARAMS)

    def write_license_key(self, key: bytes):
        data = self.connect.exchange(self.COMMAND_WRITE_LICENSE_KEY, key)
        return data

    def write_sound_info(self, number: int, sound_id: int, size: int,):
        params = int16_to_bytes(number) + int16_to_bytes(sound_id) + int32_to_bytes(size)
        self.connect.exchange(self.COMMAND_WRITE_SOUND_INFO, params)

    def write_sound_file_part(self, number: int, pos: int, data: bytes):
        params = int16_to_bytes(number) + int32_to_bytes(pos) + data
        self.connect.exchange(self.COMMAND_WRITE_SOUND_FILE, params, retry=3)

    def write_sound_file(self, number: int, file_name: str, sound_id: int,
                         model_id: int = 0, version_major: int = 0, version_minor: int = 0):
        file_size = os.path.getsize(file_name)
        self.write_sound_info(number, sound_id, file_size)

        prev_percent = 0
        with open(file_name, 'rb') as sound_file:
            curr_pos = 0
            block_size = 32

            while True:
                block = sound_file.read(block_size)
                if not block:
                    return

                self.write_sound_file_part(number, curr_pos, block)
                curr_pos += len(block)
                percent = int(curr_pos/file_size*100)
                if percent != prev_percent:
                    print("{}: {}%".format(number, percent))
                    prev_percent = percent

    def get_sound_info(self, number: int, ) -> Union[SoundInfo, None]:
        params = int16_to_bytes(number)
        data = self.connect.exchange(self.COMMAND_GET_SOUND_INFO, params, is_silent=True)
        if not data:
            return None

        return SoundInfo.unpack(data)

    def reset_sounds(self):
        self.connect.exchange(self.COMMAND_RESET_SOUNDS)

    def write_hardware_version(self, major, minor, patch):
        version = bytes([major, minor]) + int16_to_bytes(patch)
        data = self.connect.exchange(self.COMMAND_WRITE_HARDWARE_VERSION, version)
        return data

    def read_flash(self, addr=0, length=256):
        params = int32_to_bytes(addr) + int16_to_bytes(length)
        data = self.connect.exchange(self.COMMAND_READ_FLASH, params)
        return data

    def start_tests(self):
        self.connect.exchange(self.COMMAND_START_TESTS)
