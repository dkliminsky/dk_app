import logging
import serial
from PySide2.QtCore import QIODevice
from PySide2.QtSerialPort import QSerialPort, QSerialPortInfo

from .common import PortInfo


class QtSerial:
    def __init__(self):
        self.serial = None
        self.pyserial = None
        self.port_info = None

    @staticmethod
    def get_devices():
        info_list = QSerialPortInfo()
        ports = info_list.availablePorts()
        ports_info = []
        for port in ports:
            port_info = PortInfo(port, port.vendorIdentifier(), port.productIdentifier())
            ports_info.append(port_info)

        return ports_info

    def connect(self, port_obj, timeout):
        # didn't work
        # self.serial = QSerialPort(port_obj)
        # self.serial.setBaudRate(QSerialPort.Baud115200)
        # return self.serial.open(QIODevice.ReadWrite):

        logging.info('Connecting to port:', port_obj.systemLocation())
        try:
            self.pyserial = serial.Serial(port_obj.systemLocation(), baudrate=115200, timeout=timeout)
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
        # didn't work
        # data = bytes()
        # data = self.serial.readData(size)
        # return data

        return self.pyserial.read(size)

    def write(self, data: bytes):
        # didn't work
        # self.serial.writeData(data, len(data))

        self.pyserial.write(data)

