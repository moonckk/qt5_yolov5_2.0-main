from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QSlider


class Slider(QSlider):
    """
    进度条控制器
    """
    signal_valueChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super(Slider, self).__init__()

    def wheelEvent(self, e: QtGui.QWheelEvent) -> None:
        pass

    def dragMoveEvent(self, a0: QtGui.QDragMoveEvent) -> None:
        pass

    def dragLeaveEvent(self, a0: QtGui.QDragLeaveEvent) -> None:
        print(self.value())

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        current_x = event.pos().x()
        per = current_x * 1.0 / self.width()
        value = per * (self.maximum() - self.minimum()) + self.minimum()
        self.signal_valueChanged.emit(value)
