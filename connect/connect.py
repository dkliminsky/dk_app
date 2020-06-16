import time
from typing import Union

from .interfaces.qt_serial import QTSerial
from .utils import bytes_to_uint


class DKConnectError(Exception):
    pass


class DKConnectResponseTimoutError(DKConnectError):
    pass


class DKConnectCommandsMismatch(DKConnectError):
    def __init__(self, send_command, receive_command, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.send_command = send_command
        self.receive_command = receive_command


class DKConnectDisconnectedError(DKConnectError):
    pass


class DKConnectGotErrorCode(Exception):
    def __init__(self, error_code, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_code = error_code


class DKConnect:
    COMMAND_ERROR = 0xFFFF

    def __init__(self):
        self.serial = QTSerial()
        self._is_connect = False

    def is_connect(self):
        return self._is_connect

    def find_device(self, descriptions: list) -> bool:
        return self.serial.find_device(descriptions)

    def connect(self, timeout=0.1) -> bool:
        if self.serial.connect(timeout):
            self._is_connect = True
        else:
            self._is_connect = False

        return self._is_connect

    def disconnect(self):
        self._is_connect = False

    def clear(self):
        self.serial.clear()

    def device_name(self):
        return self.serial.get_description()

    def send(self, command: int, data: Union[bytes, None]):
        if not self.is_connect():
            raise DKConnectDisconnectedError

        command_size = 2
        data_size = len(data) if data else 0
        crc_size = 4
        package_size = (command_size + data_size + crc_size).to_bytes(2, byteorder='little')
        package_command = command.to_bytes(2, byteorder='little')
        package_data = data or b''

        package_crc = self._crc_stm32(package_size + package_command + package_data)
        package_crc = package_crc.to_bytes(4, byteorder='little')

        package = package_size + package_command + package_data + package_crc
        try:
            self.serial.write(package)
        except OSError:
            self._is_connect = False
            raise DKConnectError

    def receive(self):
        if not self.is_connect():
            raise DKConnectDisconnectedError

        package_size = self._read(2)
        if not package_size:
            raise DKConnectResponseTimoutError

        package_size = package_size[1] * 256 + package_size[0]

        package_command = self._read(2)
        package_command = package_command[1] * 256 + package_command[0]

        package_data = self._read(package_size - 2 - 4)

        package_crc = self._read(4)

        return package_command, package_data

    def receive_wait(self, timeout=30) -> bytes:
        start_time = time.time()
        while True:
            try:
                receive_command, receive_data = self.receive()
                return receive_data
            except DKConnectResponseTimoutError:
                pass

            if time.time() - start_time > timeout:
                raise DKConnectResponseTimoutError

            time.sleep(0.1)

    def exchange(self, command: int, data: Union[bytes, None] = None, retry=0, is_silent=False):
        if not self.is_connect():
            raise DKConnectDisconnectedError

        tries = 0
        receive_command, receive_data = None, None
        exchange_exception = None
        while True:
            tries += 1

            if tries > retry + 1:
                raise exchange_exception

            if tries > 1:
                print("Exchange error, repeat. Try:", tries)

            try:
                self.send(command, data)
                receive_command, receive_data = self.receive()
            except DKConnectError as exc:
                exchange_exception = exc
                continue

            break

        if receive_command == self.COMMAND_ERROR:
            print("Receive error: {}".format(bytes_to_uint(receive_data)))

            if not is_silent:
                raise DKConnectGotErrorCode(bytes_to_uint(receive_data))

            return None

        if receive_command != command and not is_silent:
            print("Error: send command: {}, receive command: {}".format(command, receive_command))

            if not is_silent:
                raise DKConnectCommandsMismatch(command, receive_command)

        return receive_data

    def _read(self, size: int) -> bytes:
        try:
            return self.serial.read(size)
        except (IOError, OSError):
            self._is_connect = False
            raise DKConnectError

    def _crc_stm32(self, data):
        # Computes CRC checksum using CRC-32 polynomial
        crc = 0xFFFFFFFF

        for d in data:
            crc ^= d
            for i in range(32):
                if crc & 0x80000000:
                    crc = (crc << 1) ^ 0x04C11DB7  # Polynomial used in STM32
                else:
                    crc = (crc << 1)

        return crc & 0xFFFFFFFF
