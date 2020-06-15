# import serial
# import serial.tools.list_ports


# https://pyserial.readthedocs.io/en/latest/shortintro.html

# class DKConnect:
#     COMMAND_ERROR = 256
#
#     def __init__(self, description, baudrate=9600, timeout=1.0):
#         self.description = description
#         self.baudrate = baudrate
#         self.timeout = timeout
#         self.con = None
#
#     @staticmethod
#     def list_ports():
#         return serial.tools.list_ports.comports()
#
#     @staticmethod
#     def find_device_commands():
#         return serial.tools.list_ports.comports()
#
#     def connect(self):
#         for port in self.list_ports():
#             if port.description == self.description:
#                 print('Connecting to {}...'.format(port.device))
#                 self.con = serial.Serial(port.device, baudrate=self.baudrate, timeout=self.timeout)
#                 return
#
#         self.con = None
#         print('Device not found')
#
#     def send(self, command: int, data: Union[bytes, None]):
#         if not self.con:
#             self.connect()
#
#         if not self.con:
#             return
#
#         command_size = 2
#         data_size = len(data) if data else 0
#         crc_size = 4
#         package_size = (command_size + data_size + crc_size).to_bytes(2, byteorder='little')
#         package_command = command.to_bytes(2, byteorder='little')
#         package_data = data or b''
#
#         package_crc = self._crc_stm32(package_size + package_command + package_data)
#         package_crc = package_crc.to_bytes(4, byteorder='little')
#
#         package = package_size + package_command + package_data + package_crc
#         self.con.write(package)
#
#     def receive(self):
#         if not self.con:
#             return None, None
#
#         package_size = self.con.read(2)
#         if not package_size:
#             return None, None
#         package_size = package_size[1] * 256 + package_size[0]
#
#         package_command = self.con.read(2)
#         package_command = package_command[1] * 256 + package_command[0]
#
#         package_data = self.con.read(package_size - 2 - 4)
#
#         package_crc = self.con.read(4)
#         return package_command, package_data
