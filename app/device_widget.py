from PySide2.QtWidgets import *


from app.device_worker import DeviceWorker


class LicenseWidget(QWidget):
    def __init__(self, device_worker: DeviceWorker, *args, **kwargs):
        super(LicenseWidget, self).__init__(*args, **kwargs)
        self.worker = device_worker

        self.setWindowTitle('Update license')

        self.device_id_edit = QLineEdit('n/a')
        self.device_id_edit.setReadOnly(True)
        self.key_edit = QPlainTextEdit('n/a')

        layout = QVBoxLayout()
        layout.addWidget(QLabel('Device ID'))
        layout.addWidget(self.device_id_edit)
        layout.addWidget(QLabel('License key'))
        layout.addWidget(self.key_edit)

        self.update_button = QPushButton('Update license key')
        self.update_button.clicked.connect(self._update_key)
        layout.addWidget(self.update_button)

        self.setLayout(layout)

    def set_data(self, device_id, license_key):
        self.device_id_edit.setText(device_id)
        self.key_edit.setPlainText(license_key)

    def _update_key(self):
        key = self.key_edit.toPlainText().strip()

        if len(key) != 32*2:
            QMessageBox.critical(self, 'Error', 'Invalid key length')
            return

        self.worker.add_command(self.worker.COMMAND_UPDATE_LICENSE_KEY, key)


class FirmwareWidget(QWidget):
    def __init__(self, device_worker: DeviceWorker, *args, **kwargs):
        super(FirmwareWidget, self).__init__(*args, **kwargs)
        self.worker = device_worker
        self.path_to_firmware = None

        self.worker.signals().upload_firmware_progress.connect(self._progress)
        self.worker.signals().upload_firmware_done.connect(self._done)

        self.setWindowTitle('Upload firmware')

        self.firmware_label = QLabel("")
        self.firmware_button = QPushButton('Upload firmware')
        self.firmware_button.clicked.connect(self._update)

        self.progress_label = QLabel("")
        self.progress_widget = QProgressBar()

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Upload firmware file to device:"))
        layout.addWidget(self.firmware_label)
        layout.addWidget(self.progress_label)
        layout.addWidget(self.progress_widget)
        layout.addWidget(self.firmware_button)

        self.setLayout(layout)

    def activate(self):
        self.path_to_firmware, _ = QFileDialog.getOpenFileName(self, "Load Firmware", "~/",
                                                               "DKF File (*.dkf)")

        if not self.path_to_firmware:
            return

        self.firmware_label.setText(self.path_to_firmware)
        self.progress_widget.setValue(0)
        self.firmware_button.setEnabled(True)

        self.show()

    def _update(self):
        self.worker.add_command(self.worker.COMMAND_UPDATE_FIRMWARE, self.path_to_firmware)
        self.firmware_button.setEnabled(False)

    def _progress(self, text, percent):
        self.progress_label.setText(text)
        self.progress_widget.setValue(percent)

    def _done(self):
        pass


class DeviceWidget(QWidget):
    def __init__(self, device_worker: DeviceWorker, *args, **kwargs):
        super(DeviceWidget, self).__init__(*args, **kwargs)

        self.worker = device_worker

        # Slots
        self.worker.signals().status.connect(self._status_slot)
        self.worker.signals().info.connect(self._info_slot)
        self.worker.signals().connected.connect(self._connected_slot)
        self.worker.signals().disconnected.connect(self._disconnected_slot)

        self.worker.signals().error_message.connect(self._error_message_slot)
        self.worker.signals().info_message.connect(self._info_message_slot)

        self.device_info = {}

        self.license_window = LicenseWidget(self.worker)
        self.firmware_window = FirmwareWidget(self.worker)

        self.status_label = QLabel("n/a")
        self.name_label = QLabel("n/a")
        self.soft_version_label = QLabel("n/a")
        self.hard_version_label = QLabel("n/a")
        self.license_label = QLabel("n/a")

        self.reset_button = QPushButton('Reset device')
        self.set_license_button = QPushButton('Set license key...')
        self.firmware_button = QPushButton('Upload firmware...')
        self.bootloader_check = QCheckBox('Switch to bootloader')

        self._make_widgets()
        self._disconnected_slot()

    def _make_widgets(self):
        self.device_layout = QHBoxLayout()

        self.info_layout = QVBoxLayout()
        self._add_info_line('Status:', self.status_label)
        self._add_info_line('Name:', self.name_label)
        self._add_info_line('Software version:', self.soft_version_label)
        self._add_info_line('Hardware version:', self.hard_version_label)
        self._add_info_line('License:', self.license_label)
        self.info_layout.addStretch(1)
        self.device_layout.addLayout(self.info_layout)

        self.command_layout = QVBoxLayout()
        self.command_layout.addWidget(self.reset_button)
        self.command_layout.addWidget(self.set_license_button)
        self.command_layout.addWidget(self.firmware_button)
        self.command_layout.addWidget(self.bootloader_check)
        self.command_layout.addStretch(1)
        self.device_layout.addLayout(self.command_layout)

        self.set_license_button.clicked.connect(self._set_license)
        self.reset_button.clicked.connect(self._reset)
        self.firmware_button.clicked.connect(self._firmware)
        self.bootloader_check.stateChanged.connect(self._activate_bootloader_click)

        self.setLayout(self.device_layout)

    def _add_info_line(self, name, layout):
        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel(name))
        h_layout.addWidget(layout)
        self.info_layout.addLayout(h_layout)

    def _set_license(self):
        self.license_window.set_data(self.device_info.get('uid', 'n/a'), self.device_info.get('key', 'n/a'),)
        self.license_window.show()

    def _reset(self):
        self.worker.add_command(self.worker.COMMAND_RESET)

    def _firmware(self):
        self.firmware_window.activate()

    def _activate_bootloader_click(self, state):
        self.worker.activate_bootloader(bool(state))

    def _status_slot(self, text):
        self.status_label.setText(text)

    def _info_slot(self, info: dict):
        self.device_info = info
        self.name_label.setText(info.get('name', 'n/a'))
        self.soft_version_label.setText(info.get('soft_version', 'n/a'))
        self.hard_version_label.setText(info.get('hard_version', 'n/a'))
        self.license_label.setText(info.get('license', 'n/a'))

    def _connected_slot(self):
        self.firmware_button.setEnabled(True)
        self.reset_button.setEnabled(True)

        if not self.worker.is_bootloader():
            self.set_license_button.setEnabled(True)

    def _disconnected_slot(self):
        self.name_label.setText('n/a')
        self.soft_version_label.setText('n/a')
        self.hard_version_label.setText('n/a')
        self.license_label.setText('n/a')
        self.set_license_button.setEnabled(False)
        self.reset_button.setEnabled(False)
        self.firmware_button.setEnabled(False)

    def _error_message_slot(self, text):
        QMessageBox.critical(self, 'Error', text)

    def _info_message_slot(self, text):
        QMessageBox.information(self, 'Info', text)

