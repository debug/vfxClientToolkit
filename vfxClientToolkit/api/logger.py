import logging
import logging.handlers
import os
import datetime
from typing import Dict
from vfxClientToolkit import __title__
import tempfile


def get_log_dir():
    temp_dir = tempfile.gettempdir()
    log_dir = os.path.join(temp_dir, "logs")
    if os.path.exists(log_dir) == False:
        os.mkdir(log_dir)

    return log_dir


class SingletonType(type):
    _instances: Dict[object, object] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonType, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class CustomLogger(object, metaclass=SingletonType):

    _logger = None

    def __init__(self):
        self._logger = logging.getLogger(__title__)
        self._logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s \t [%(levelname)s | %(filename)s:%(lineno)s] > %(message)s"
        )

        now = datetime.datetime.now()
        # TODO fix this!
        dirname = get_log_dir()
        if not os.path.isdir(dirname):
            os.mkdir(dirname)
        fileHandler = logging.handlers.RotatingFileHandler(
            dirname + "/log_" + now.strftime("%Y-%m-%d") + ".log"
        )

        streamHandler = logging.StreamHandler()

        fileHandler.setFormatter(formatter)
        streamHandler.setFormatter(formatter)

        self._logger.addHandler(fileHandler)
        self._logger.addHandler(streamHandler)

    def get_logger(self):
        return self._logger


def getLogger():
    logObj = CustomLogger()
    return logObj.get_logger()
