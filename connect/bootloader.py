import logging
import os

from .commands import DKGeneralCommands
from .utils import bytes_to_float, bytes_to_uint, int16_to_bytes, int32_to_bytes, float_to_bytes, int8_to_bytes


UPLOAD_ATTEMPTS = 5


class DKBootloaderFirmwareNotAligned(Exception):
    pass


class DKBootloaderCommands(DKGeneralCommands):
    DEVICE_NAME = 'DK Bootloader'

    # Bootloader
    COMMAND_CONFIRM_BOOTLOADER = 200
    COMMAND_GO_TO_APP = 201

    # Program MCU flash
    COMMAND_ERASE = 210
    COMMAND_WRITE = 211
    COMMAND_CALC_MD5 = 212

    # Program external flash
    COMMAND_FLASH_PARAMS_ERASE = 220
    COMMAND_FLASH_SOUNDS_ERASE = 221

    WRITE_BLOCK_SIZE = 16
    FIRMWARE_MD5_SIZE = 16

    def confirm(self):
        self.connect.exchange(self.COMMAND_CONFIRM_BOOTLOADER, None)

    def go_to_app(self):
        self.connect.send(self.COMMAND_GO_TO_APP, None)
        self.connect.disconnect()

    def flash_update(self, file_name: str):
        print('Erasing flash...')
        self.flash_erase()

        print('Writing to flash...')
        gen = self.flash_write_async(file_name)

        try:
            while True:
                percent = next(gen)
                print(percent)
        except StopIteration:
            pass

        logging.info('Checking flash...')

        if self.flash_check(file_name):
            print('Firmware updated successfully.')
        else:
            print('ERROR! Firmware checksum mismatch!')

    def flash_erase(self) -> int:
        self.connect.send(self.COMMAND_ERASE, None)
        _, data = self.connect.receive_wait()
        bad_blocks = bytes_to_uint(data)
        return bad_blocks

    def flash_write_part(self, pos: int, data: bytes):
        params = int32_to_bytes(pos) + data
        self.connect.exchange(self.COMMAND_WRITE, params, retry=UPLOAD_ATTEMPTS)

    def flash_write_async(self, file_name: str):
        file_size = os.path.getsize(file_name)
        logging.info('Firmware file size: {}'.format(file_size))
        prev_percent = 0

        with open(file_name, 'rb') as firmware_file:
            curr_pos = 0
            firmware_file.read(4)
            firmware_file.read(self.FIRMWARE_MD5_SIZE)

            while True:
                block = firmware_file.read(self.WRITE_BLOCK_SIZE)
                if not block:
                    return

                if len(block) < self.WRITE_BLOCK_SIZE:
                    logging.error('File not aligned to {}} bytes!'.format(self.WRITE_BLOCK_SIZE))
                    raise DKBootloaderFirmwareNotAligned

                self.flash_write_part(curr_pos, block)
                curr_pos += len(block)
                percent = int(curr_pos/file_size*100)
                if percent != prev_percent:
                    prev_percent = percent
                    yield percent

    def flash_check(self, file_name: str) -> bool:

        with open(file_name, 'rb') as firmware_file:
            firmware_size = bytes_to_uint(firmware_file.read(4))
            file_md5 = firmware_file.read(self.FIRMWARE_MD5_SIZE)

        flash_md5 = self.calc_md5(firmware_size)
        logging.info('File MD5: {}'.format(file_md5.hex()))
        logging.info('Flash MD5: {}'.format(flash_md5.hex()))
        return file_md5 == flash_md5

    def calc_md5(self, flash_size: int) -> bytes:
        params = int32_to_bytes(flash_size)
        data = self.connect.exchange(self.COMMAND_CALC_MD5, params)
        return data
