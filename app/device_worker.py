import logging
import queue
import time

from PySide2.QtCore import QRunnable, Slot, QObject, Signal

from connect import DKConnect, DKTankCommands, DKConnectError, DKConnectCommandsMismatch, DKConnectGotErrorCode, \
    DKConnectResponseTimoutError, DKBootloaderCommands, DEVICES_ESSENTIAL_LIST, build_commands, DEVICE_BOOTLOADER


class DeviceWorkerSignals(QObject):
    status = Signal(str)
    info = Signal(dict)
    connected = Signal()
    disconnected = Signal()

    upload_firmware_progress = Signal(str, int)
    upload_firmware_done = Signal()

    error_message = Signal(str)
    info_message = Signal(str)


class DeviceWorker(QRunnable):
    LICENSE_LIST = {
        0: 'No license',
        1: 'Lite',
        2: 'Standard',
        3: 'Pro',
    }

    COMMAND_RESET = 'reset'
    COMMAND_UPDATE_LICENSE_KEY = 'update_license_key'
    COMMAND_UPDATE_FIRMWARE = 'update_firmware'

    PROGRESS_ACTIVATE_BOOTLOADER = 'Activate Bootloader...'
    PROGRESS_ERASE_FLASH = 'Erase memory...'
    PROGRESS_WRITE_FLASH = 'Write firmware...'
    PROGRESS_CHECK_FLASH = 'Check firmware...'
    PROGRESS_FIRMWARE_DONE = 'Upload done'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._signals = DeviceWorkerSignals()

        self.connect = DKConnect()
        self.is_activate_bootloader = False
        self.cmd = None
        self.queue = queue.Queue()
        self.ping_elapsed_time = 0
        self.is_stop = False

    def stop(self):
        self.is_stop = True

    def signals(self) -> DeviceWorkerSignals:
        return self._signals

    def activate_bootloader(self, activate: bool):
        self.is_activate_bootloader = activate

        if self.connect.is_connect():
            self.cmd.system_reset()

        self._disconnected()

    def is_bootloader(self) -> bool:
        return self.cmd.device_name() == DEVICE_BOOTLOADER

    def is_essential(self) -> bool:
        return self.cmd.device_name() in DEVICES_ESSENTIAL_LIST

    def add_command(self, command_name: str, command_params=None):
        self.queue.put((command_name, command_params))

    @Slot()
    def run(self):
        while True:

            try:
                if self.connect.is_connect():
                    self._run_connected()
                else:
                    self._run_connecting()

            except DKConnectCommandsMismatch:
                self.connect.clear()
            except DKConnectError:
                self._disconnected()

            if self.is_stop:
                break

    def _run_connected(self):
        # Check that the device is connected
        curr_time = time.time()
        if curr_time - self.ping_elapsed_time > 1:
            self.ping_elapsed_time = curr_time
            self.cmd.ping()

        # Run commands
        if self.connect.is_connect() and not self.queue.empty():
            self._run_command()

        time.sleep(0.1)

    def _run_connecting(self):
        while True:
            if self.connect.find_and_connect():
                self.cmd = build_commands(self.connect)

                if self.cmd.device_name() == DEVICE_BOOTLOADER:

                    if self.is_activate_bootloader:
                        self.cmd.confirm()
                    else:
                        self.cmd.go_to_app()
                        time.sleep(0.1)
                        continue

                self.signals().status.emit('Connected')
                self.signals().connected.emit()
                self._update_general_info()
                return

            if self.is_stop:
                return

            self.signals().status.emit('Wait for device...')
            time.sleep(1)

    def _update_general_info(self):
        info = {
            'name': self.cmd.get_name(),
            'uid': self.cmd.get_uid().hex(),
            'soft_version': '.'.join(str(x) for x in self.cmd.get_software_version()),
        }

        if self.is_essential():
            info['hard_version'] = '.'.join(str(x) for x in self.cmd.get_hardware_version())
            info['uid'] = self.cmd.get_uid().hex()
            info['key'] = self.cmd.get_license_key().hex()
            info['license'] = self.LICENSE_LIST.get(self.cmd.get_access_level(), 'unknown')

        self.signals().info.emit(info)

    def _disconnected(self):
        self.signals().disconnected.emit()

    def _run_command(self):
        command = self.queue.get(block=False, timeout=None)
        self.queue.task_done()
        command_name, command_params = command

        try:
            if command_name == self.COMMAND_RESET:
                self.cmd.system_reset()
                time.sleep(1)
                self._disconnected()
            elif command_name == self.COMMAND_UPDATE_LICENSE_KEY:
                self._update_license(command_params)
            elif command_name == self.COMMAND_UPDATE_FIRMWARE:
                self._upload_firmware(command_params)
                self.signals().upload_firmware_done.emit()

        except DKConnectGotErrorCode as exc:
            self.signals().error_message.emit('Received error from device, code: {}'.format(exc.error_code))

    def _update_license(self, license_key):
        try:
            license_key = bytes.fromhex(license_key)
        except ValueError:
            self.signals().error_message.emit('Key format error!')
            return

        self.cmd.write_license_key(license_key)
        self.signals().info_message.emit('License key updated successfully. Reset the device.')

    def _upload_firmware(self, path_to_firmware):
        logging.info('Starting upload firmware')
        self.signals().upload_firmware_progress.emit(self.PROGRESS_ACTIVATE_BOOTLOADER, 0)

        is_return_to_essential = not self.is_activate_bootloader

        if not self.is_bootloader():
            logging.info('Reset to bootloader')
            self.cmd.system_reset()
            self._disconnected()

            time.sleep(1)
            self.signals().upload_firmware_progress.emit(self.PROGRESS_ACTIVATE_BOOTLOADER, 33)

            time.sleep(1)
            self.signals().upload_firmware_progress.emit(self.PROGRESS_ACTIVATE_BOOTLOADER, 66)

            self.activate_bootloader(True)
            logging.info('Connecting to bootloader')
            self._run_connecting()

        logging.info('Erasing flash')
        self.signals().upload_firmware_progress.emit(self.PROGRESS_ERASE_FLASH, 0)
        self.cmd.flash_erase()

        logging.info('Writing to flash')
        self.signals().upload_firmware_progress.emit(self.PROGRESS_WRITE_FLASH, 0)
        gen = self.cmd.flash_write_async(path_to_firmware)

        try:
            while True:
                percent = next(gen)
                self.signals().upload_firmware_progress.emit(self.PROGRESS_WRITE_FLASH, percent)

                if self.is_stop:
                    break

        except StopIteration:
            pass

        logging.info('Checking flash')
        self.signals().upload_firmware_progress.emit(self.PROGRESS_CHECK_FLASH, 0)

        if self.cmd.flash_check(path_to_firmware):
            self.signals().info_message.emit('Firmware updated successfully.')
        else:
            self.signals().error_message.emit('Firmware checksum mismatch!')
            return

        self.signals().upload_firmware_progress.emit(self.PROGRESS_FIRMWARE_DONE, 100)

        if is_return_to_essential:
            logging.info('Returning to main firmware')
            self.activate_bootloader(False)
