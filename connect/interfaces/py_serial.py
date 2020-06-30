import logging
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
        logging.info('Connecting to port: {}'.format(port_obj.usb_info()))
        try:
            self.pyserial = serial.Serial(port_obj.device, baudrate=115200, timeout=timeout)
        except (FileNotFoundError, OSError) as exc:
            logging.debug('Connecting error', exc_info=True)
            return False

        return bool(self.pyserial)

    def close(self):
        if self.pyserial:
            self.pyserial.close()

    def clear(self):
        if not self.pyserial:
            return

        self.pyserial.reset_input_buffer()
        self.pyserial.reset_output_buffer()

    def read(self, size: int) -> bytes:
        return self.pyserial.read(size)

    def readline(self) -> bytes:
        return self.pyserial.readline()

    def write(self, data: bytes):
        self.pyserial.write(data)
