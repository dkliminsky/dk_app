import serial

from PySide2.QtCore import QIODevice
from PySide2.QtSerialPort import QSerialPort, QSerialPortInfo


class QTSerial:
    def __init__(self):
        self.serial = None
        self.pyserial = None
        self.port_info = None

    def get_description(self):
        return self.port_info.description()

    def find_device(self, devices_list: list):
        info_list = QSerialPortInfo()
        ports = info_list.availablePorts()
        for port in ports:
            # print('Found port:', port.systemLocation())
            if port.description() in devices_list:
                self.port_info = port
                return True

        return False

    def clear(self):
        if not self.pyserial:
            return

        self.pyserial.reset_input_buffer()
        self.pyserial.reset_output_buffer()

    def connect(self, timeout):
        if not self.port_info:
            return

        # self.serial = QSerialPort(port)
        # self.serial.setBaudRate(QSerialPort.Baud115200)
        # if not self.serial.open(QIODevice.ReadWrite):
        #     raise IOError("Cannot connect to device")

        # print('Connecting to port:', self.port_info.systemLocation())
        self.pyserial = serial.Serial(self.port_info.systemLocation(), baudrate=115200, timeout=timeout)
        if self.pyserial:
            is_connect = True
        else:
            is_connect = False

        return is_connect

    def read(self, size: int) -> bytes:
        # data = bytes()
        # data = self.serial.readData(size)
        # return data
        return self.pyserial.read(size)

    def write(self, data: bytes):
        # self.serial.writeData(data, len(data))
        self.pyserial.write(data)

