import os
import PySide2

dirname = os.path.dirname(PySide2.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path

from PySide2.QtCore import QThreadPool
from PySide2.QtWidgets import *

from app.device_widget import DeviceWidget
from app.device_worker import DeviceWorker


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.device_worker = DeviceWorker()
        self.device_widget = DeviceWidget(self.device_worker)

        self.threadpool = QThreadPool()
        self.threadpool.start(self.device_worker)

        self.setWindowTitle("DK App")

        layout1 = QHBoxLayout()

        layout1.addWidget(self.device_widget)

        widget = QWidget()
        widget.setLayout(layout1)
        self.setCentralWidget(widget)

    def closeEvent(self, event):
        self.device_worker.stop()
        super().closeEvent(event)


if __name__ == '__main__':
    app = QApplication([])
    main_window = MainWindow()
    main_window.show()
    app.exec_()
