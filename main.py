# https://www.learnpyqt.com/
# Terminal example: https://iosoft.blog/2019/04/30/pyqt-serial-terminal/
#
from PySide2.QtCore import QThreadPool
from PySide2.QtWidgets import *

from app.device_widget import DeviceWidget
from app.device_worker import DeviceWorker


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        device_worker = DeviceWorker()
        device_widget = DeviceWidget(device_worker)

        self.threadpool = QThreadPool()
        self.threadpool.start(device_worker)

        self.setWindowTitle("DK App")

        layout1 = QHBoxLayout()

        layout1.addWidget(device_widget)

        widget = QWidget()
        widget.setLayout(layout1)
        self.setCentralWidget(widget)


if __name__ == '__main__':
    app = QApplication([])
    main_window = MainWindow()
    main_window.show()
    app.exec_()
