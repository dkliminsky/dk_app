import serial
from serial.tools import list_ports

from .common import PortInfo


class PySerial:

    def __init__(self):
        self.serial = None
        self.pyserial = None
        self.port_info = None

    @staticmethod
    def get_devices():
        ports_info = []
        for port in list_ports.comports():
            port_info = PortInfo(port, port.vid, port.pid)
            ports_info.append(port_info)

        return ports_info

    def connect(self, port_obj, timeout):
        print('Connecting to port:', port_obj.usb_info())
        try:
            self.pyserial = serial.Serial(port_obj, baudrate=115200, timeout=timeout)
        except OSError as exc:
            print('os error', str(exc))
            return False

        return bool(self.pyserial)

    def clear(self):
        if not self.pyserial:
            return

        self.pyserial.reset_input_buffer()
        self.pyserial.reset_output_buffer()

    def read(self, size: int) -> bytes:
        return self.pyserial.read(size)

    def write(self, data: bytes):
        self.pyserial.write(data)
