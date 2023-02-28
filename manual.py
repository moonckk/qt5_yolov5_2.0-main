import time

import cv2
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QFileDialog

from logger.logger import get_logger
from slider import Slider
from timer import VideoTimer
from ui.ui_manual import Ui_manual

logger = get_logger("logger")


class Manual(QMainWindow, Ui_manual):

    def __init__(self):
        super(Manual, self).__init__()
        self.setupUi(self)

        self.raw_video_url = ""
        self.raw_capture = cv2.VideoCapture()  # 原视频播放器
        self.raw_window_name = "raw"
        self.raw_video_fps = 0
        self.raw_video_total_frames = 0
        self.raw_video_height = 0
        self.raw_video_width = 0

        self.auto_video_url = ""
        self.auto_capture = cv2.VideoCapture()  # 自动标注视频播放器
        self.auto_window_name = "auto"
        self.auto_video_fps = 0
        self.auto_video_total_frames = 0
        self.auto_video_height = 0
        self.auto_video_width = 0

        self.num = None
        self.slider = None

        self.timer = VideoTimer()
        self.timer.signal_update_frame.connect(self.video_play)
        self.timer.signal_finished.connect(self.video_paused)

        # cv中实现的追踪器
        self.OPENCV_OBJECT_TRACKERS = {
            "csrt": cv2.TrackerCSRT_create,
            "kcf": cv2.TrackerKCF_create,
            "boosting": cv2.TrackerBoosting_create,
            "mil": cv2.TrackerMIL_create,
            "tld": cv2.TrackerTLD_create,
            "medianflow": cv2.TrackerMedianFlow_create,
            "mosse": cv2.TrackerMOSSE_create
        }
        self.trackers = None
        self.current_auto_frame = None

        self.is_save_video = False  # 是否保存视频
        self.btn_save.setText("开始录制")
        self.save_video = None

        self.set_layouts()
        self.set_actions()

    def set_layouts(self):
        # 此处用封装的Slider
        self.slider = Slider(self.centralwidget)
        self.slider.setEnabled(True)
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.slider.setObjectName("slider")
        self.gridLayout.addWidget(self.slider, 0, 0, 1, 1)

    def set_actions(self):
        self.btn_open_raw_video.clicked.connect(self.open_raw_video)
        self.btn_open_auto_video.clicked.connect(self.open_auto_video)
        self.btn_play.clicked.connect(self.action_play)
        self.slider.signal_valueChanged.connect(self.video_jump)
        self.btn_mark.clicked.connect(self.mark)
        self.btn_unmark.clicked.connect(self.unmark)
        # 保存视频
        self.btn_save.clicked.connect(self.action_save)
        self.btn_unsave.clicked.connect(self.action_export)

    def open_raw_video(self):
        file, _ = QFileDialog.getOpenFileName(self, '打开视频', '../', '视频文件(*.mp4)')
        if len(file) < 1:
            self.label_raw_video_path.setText("null")
            return
        self.raw_video_url = file
        self.label_raw_video_path.setText(file)
        if self.raw_video_url and self.auto_video_url:
            self.action_reset()

    def open_auto_video(self):
        file, _ = QFileDialog.getOpenFileName(self, '打开视频', '../', '视频文件(*.mp4)')
        if len(file) < 1:
            self.label_auto_video_path.setText("null")
            return
        self.auto_video_url = file
        self.label_auto_video_path.setText(file)
        if self.raw_video_url and self.auto_video_url:
            self.action_reset()

    def action_save(self):
        if self.is_save_video:
            self.btn_save.setText("开始录制")
            self.is_save_video = False
        else:
            self.btn_save.setText("结束录制")
            self.is_save_video = True
            if self.save_video is None:
                self.save_video = cv2.VideoWriter()
                fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')  # mp4编码
                sz = (int(self.raw_video_width),
                      int(self.raw_video_height))
                self.save_video.open(f"output_{int(time.time())}.mp4", fourcc, self.raw_video_fps, sz, True)

    def action_export(self):
        self.is_save_video = False
        if self.save_video is not None:
            self.save_video.release()
            self.statusbar.showMessage("导出成功")
            self.btn_save.setText("开始录制")
            self.is_save_video = False

    def action_reset(self):
        self.raw_capture.open(self.raw_video_url)
        self.raw_video_fps = self.raw_capture.get(cv2.CAP_PROP_FPS)
        self.raw_video_total_frames = self.raw_capture.get(cv2.CAP_PROP_FRAME_COUNT)
        self.raw_video_height = self.raw_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.raw_video_width = self.raw_capture.get(cv2.CAP_PROP_FRAME_WIDTH)

        self.auto_capture.open(self.auto_video_url)
        self.auto_video_fps = self.auto_capture.get(cv2.CAP_PROP_FPS)
        self.auto_video_total_frames = self.auto_capture.get(cv2.CAP_PROP_FRAME_COUNT)
        self.auto_video_height = self.auto_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.auto_video_width = self.auto_capture.get(cv2.CAP_PROP_FRAME_WIDTH)

        self.num = None
        self.timer.fps = self.raw_video_fps
        self.spin.setSuffix(f'/{self.raw_video_total_frames}')
        self.spin.setMaximum(self.raw_video_total_frames)
        self.slider.setMaximum(self.raw_video_total_frames)
        self.video_play()

    def action_play(self):
        if self.raw_capture.isOpened() and self.auto_capture.isOpened():
            [self.timer.start, self.timer.pause][self.timer.playing]()
        elif self.raw_video_url and self.auto_video_url:
            self.action_reset()
        if self.btn_play.text() == '播放':
            self.btn_play.setText('暂停')
        else:
            self.btn_play.setText('播放')

    def video_jump(self, num):
        self.num = num
        self.slider.setValue(num)
        self.spin.setValue(num)
        self.get_frame(num)

    def video_paused(self):
        if self.num >= self.raw_video_total_frames:
            self.action_reset()

    def video_play(self):
        if self.num is None:
            self.num = self.raw_capture.get(cv2.CAP_PROP_POS_FRAMES) + 1
        else:
            self.num += 1
        self.slider.setValue(self.num)
        self.spin.setValue(self.num)
        self.get_frame()

    def get_frame(self, num=None):
        if self.raw_capture.isOpened() and self.auto_capture.isOpened():
            if num is not None:
                self.raw_capture.set(cv2.CAP_PROP_POS_FRAMES, num)
                self.auto_capture.set(cv2.CAP_PROP_POS_FRAMES, num)
            raw_success, raw_frame = self.raw_capture.read()
            auto_success, auto_frame = self.auto_capture.read()
            if raw_success and auto_success:
                self.current_auto_frame = auto_frame
                # 如果使用了追踪器,需要用追踪器更新原视频帧
                if self.trackers is not None:
                    update_raw_success, boxes = self.trackers.update(raw_frame)
                    if update_raw_success:
                        for box in boxes:
                            (x, y, w, h) = [int(v) for v in box]
                            cv2.rectangle(raw_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                # 显示
                cv2.imshow(self.raw_window_name, raw_frame)
                cv2.imshow(self.auto_window_name, auto_frame)
                # 保存视频
                if self.save_video is not None and self.is_save_video:
                    self.save_video.write(raw_frame)

    def mark(self):
        self.btn_unmark.setEnabled(False)
        self.btn_mark.setEnabled(False)
        self.btn_play.setEnabled(False)
        self.trackers = cv2.MultiTracker_create()
        if self.timer.playing:
            self.action_play()
        if self.current_auto_frame is None:
            return
        auto_frame = self.current_auto_frame
        # 在自动标注帧上画框
        box = cv2.selectROI(self.auto_window_name, auto_frame, fromCenter=False, showCrosshair=True)
        # 设置一个追踪器,也可以选择别的追踪器,有不同的效果
        tracker = self.OPENCV_OBJECT_TRACKERS["mosse"]()
        # 使用自动标注的帧训练追踪器
        self.trackers.add(tracker, auto_frame, box)
        self.btn_unmark.setEnabled(True)
        self.btn_mark.setEnabled(True)
        self.btn_play.setEnabled(True)

    def unmark(self):
        self.trackers = None
