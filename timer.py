import time

from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QMutexLocker


class VideoTimer(QThread):
    signal_update_frame = pyqtSignal()
    signal_finished = pyqtSignal()

    def __init__(self):
        super(VideoTimer, self).__init__()
        self.playing = False
        self.fps = 0
        self.mutex = QMutex()

    def run(self):
        with QMutexLocker(self.mutex):
            self.playing = True
        while self.playing:
            self.signal_update_frame.emit()
            # 控制视频播放速度
            time.sleep(1 / self.fps)
        self.signal_finished.emit()

    def pause(self):
        with QMutexLocker(self.mutex):
            self.playing = False
