import logging
import os
import PySide2

dirname = os.path.dirname(PySide2.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path

from PySide2 import QtCore
from PySide2 import QtWidgets

from app.device_widget import DeviceWidget
from app.device_worker import DeviceWorker


LOG_FILE = 'dk_app.log'


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.device_worker = DeviceWorker()
        self.device_widget = DeviceWidget(self.device_worker)

        self.threadpool = QtCore.QThreadPool()
        self.threadpool.start(self.device_worker)

        self.setWindowTitle("DK App")

        layout1 = QtWidgets.QHBoxLayout()

        layout1.addWidget(self.device_widget)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout1)
        self.setCentralWidget(widget)

    def closeEvent(self, event):
        self.device_worker.stop()
        super().closeEvent(event)


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(LOG_FILE)
    logger.addHandler(file_handler)

    logging.info('Started DK App')
    app = QtWidgets.QApplication([])
    main_window = MainWindow()
    main_window.show()
    app.exec_()
