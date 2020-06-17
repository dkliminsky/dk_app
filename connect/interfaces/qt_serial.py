import serial
from serial.tools import list_ports
from PySide2.QtCore import QIODevice
from PySide2.QtSerialPort import QSerialPort, QSerialPortInfo

from interfaces.common import PortInfo


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
        # self.serial = QSerialPort(port_obj)
        # self.serial.setBaudRate(QSerialPort.Baud115200)
        # return self.serial.open(QIODevice.ReadWrite):

        print('Connecting to port:', port_obj.systemLocation())
        try:
            self.pyserial = serial.Serial(port_obj.systemLocation(), baudrate=115200, timeout=timeout)
        except OSError as exc:
            return False

        return bool(self.pyserial)

    def clear(self):
        if not self.pyserial:
            return

        self.pyserial.reset_input_buffer()
        self.pyserial.reset_output_buffer()

    # def find_device(self, devices_list: list):
    #     info_list = QSerialPortInfo()
    #     ports = info_list.availablePorts()
    #     for port in ports:
    #         # print('Found port:', port.systemLocation())
    #         if port.vendorIdentifier() == self.vid and port.productIdentifier() == self.pid:
    #             self.port_info = port
    #             return True
    #
    #     return False

    # def connect(self, timeout):
    #     if not self.port_info:
    #         return
    #
    #     # self.serial = QSerialPort(port)
    #     # self.serial.setBaudRate(QSerialPort.Baud115200)
    #     # if not self.serial.open(QIODevice.ReadWrite):
    #     #     raise IOError("Cannot connect to device")
    #
    #     # print('Connecting to port:', self.port_info.systemLocation())
    #     self.pyserial = serial.Serial(self.port_info.systemLocation(), baudrate=115200, timeout=timeout)
    #     if self.pyserial:
    #         is_connect = True
    #     else:
    #         is_connect = False
    #
    #     return is_connect

    def read(self, size: int) -> bytes:
        # data = bytes()
        # data = self.serial.readData(size)
        # return data
        return self.pyserial.read(size)

    def write(self, data: bytes):
        # self.serial.writeData(data, len(data))
        self.pyserial.write(data)

