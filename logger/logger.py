"""
可以使用get_logger创建日志对象,该日志对象包含了控制台日志处理器和日志文件处理器
可以在这里设置日志级别,默认是DEBUG
"""

import logging
import sys
import os
from logging.handlers import TimedRotatingFileHandler

path = os.path.split(os.path.abspath(__file__))[0]
FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s "
                              "- %(module)s - %(funcName)s - %(lineno)d ")
LOG_FILE = path + "/logs.log"


def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler


def get_file_handler():
    file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight', encoding="utf-8")
    file_handler.setFormatter(FORMATTER)
    return file_handler


def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)  # better to have too much log than not enough
    logger.addHandler(get_console_handler())
    logger.addHandler(get_file_handler())
    # with this pattern, it's rarely necessary to propagate the error up to parent
    logger.propagate = False
    return logger
