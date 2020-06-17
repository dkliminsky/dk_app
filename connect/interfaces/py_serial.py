import serial
from serial.tools import list_ports


class PySerial:

    def __init__(self, vid, pid):
        self.vid = vid
        self.pid = pid
        self.serial = None
        self.pyserial = None
        self.port_info = None

    def find_device(self, devices_list: list):
        for port in list_ports.comports():
            if port.vid == self.vid and port.pid == self.pid:
                self.port_info = port
                return True
                # print(port.device, port.pid, port.vid)

        # info_list = QSerialPortInfo()
        # ports = info_list.availablePorts()
        # for port in ports:
        #     # print('Found port:', port.systemLocation())
        #     if port.description() in devices_list:
        #         self.port_info = port
        #         return True

        return False

    def clear(self):
        if not self.pyserial:
            return

        self.pyserial.reset_input_buffer()
        self.pyserial.reset_output_buffer()

    def connect(self, timeout):
        if not self.port_info:
            return

        print('Connecting to port:', self.port_info.location)
        self.pyserial = serial.Serial(self.port_info.location, baudrate=115200, timeout=timeout)
        if self.pyserial:
            is_connect = True
        else:
            is_connect = False

        return is_connect

    def read(self, size: int) -> bytes:
        return self.pyserial.read(size)

    def write(self, data: bytes):
        self.pyserial.write(data)

