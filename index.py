from PyQt5.QtWidgets import QMainWindow
from PyQt5 import QtWidgets, QtCore, QtGui
import cv2
from logger.logger import get_logger
from manual import Manual
from ui.ui_index import Ui_index
from PyQt5.QtWidgets import *
from detect_qt5 import v5detect
logger = get_logger("logger")


class Index(QMainWindow, Ui_index):

    def __init__(self):
        super(Index, self).__init__()
        self.pgb=QProgressBar(self)  #类对象的初始化
        self.pgb.setHidden(True)
        self.pgb.move(60,90)   #将进度条移动到指定位置
        self.pgb.resize(200,20)   #设置进度条宽高
        self.pgb.setMinimum(0)
        self.pgb.setMaximum(100)
        self.pgb.setValue(0) 
        self.setupUi(self)
        self.manual = None
        self.set_layouts()
        self.set_actions()
        self.v5 = v5detect()
        # self.timer_camera4 = QtCore.QTimer()
    def open_video_button(self):
        imgName, imgType = QFileDialog.getOpenFileName(self, "打开视频", "", "*.mp4;;*.AVI;;*.rmvb;;All Files(*)")
        video = cv2.VideoCapture(imgName)
        
    # img = cv2.imread(r'D:\qt5_yolov5_2.0-main\555.jpg')
        # video = cv2.VideoCapture(r"D:\qt5_yolov5_2.0-main\fb1d443f0d26b38a00f7a57355111be2.mp4")
        length = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    
        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        cap_fps = video.get(cv2.CAP_PROP_FPS)
        str = imgName.replace(".mp4","")
        str = str.replace(".AVI","")
        str = str.replace(".rmvb","")
        video1 = cv2.VideoWriter(str+'_result.mp4', fourcc, cap_fps, (frame_width,frame_height))
        i = 0
        self.pgb.setHidden(False)
        self.pgb.setValue(0) 
        while(True):
            flag, image1 = video.read()
            if flag == True:
                res,im0 = self.v5.detect(image1)
                video1.write(im0)
                cv2.imwrite("aa.jpg",im0)
                i = i+1
                self.pgb.setValue((i/length)*100) 
                QApplication.processEvents()
            # print(i)
            # i = i+1
            else:
              
                break
        self.pgb.setValue(100) 
        video1.release()
        
    def set_layouts(self):
        """"""

    def set_actions(self):
        """"""
        self.btn_manual.clicked.connect(self.manual_mark)
        self.btn_auto.clicked.connect(self.open_video_button)

    def manual_mark(self):
        """打开人工标记窗体"""
        self.manual = Manual()
        self.manual.show()
