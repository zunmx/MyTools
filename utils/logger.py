#!/usr/bin/python
# -*-coding:utf-8-*-
import logging
import os
import threading
import datetime
import time
import inspect


class Logger(object):
    __logger = None

    def __new__(cls, *args, **kwargs):
        if cls.__logger is None:
            cls.__logger = object.__new__(cls)
            cls.lock = threading.Lock()
            cls.logger = logging.getLogger("")
            logFolder = os.path.join(os.getcwd(), 'logs')
            if not os.path.exists(logFolder):
                os.makedirs(logFolder)
            timestamp = time.strftime("%Y-%m-%d", time.localtime())
            logfilename = '%s.txt' % timestamp
            logFile = os.path.join(os.getcwd(), 'logs', logfilename)
            logging.basicConfig(filename=logFile,
                                level=logging.DEBUG,
                                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        return cls.__logger

    def __init__(self, process=''):
        pass

    def info(self, message):
        self.aim()
        msg = self.process + " ---> " + message
        self.__print('[INFO]', msg)
        self.logger.info(msg)

    def debug(self, message):
        self.aim()
        msg = self.process + " ---> " + message
        self.__print('[DEBUG]', msg)
        self.logger.debug(msg)

    def warning(self, message):
        self.aim()
        msg = self.process + " ---> " + message
        self.__print('[WARN]', msg)
        self.logger.warning(msg)

    def error(self, message):
        self.aim()
        msg = self.process + " ---> " + message
        self.__print('[ERROR]', msg)
        self.logger.error(msg)

    def __print_inner(self, t, m):
        self.lock.acquire()
        print(datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S:%f"), t, m)
        self.lock.release()

    def __print(self, t, m):
        threading.Thread(target=self.__print_inner, args=(t, m,)).start()

    def aim(self):
        tmp = inspect.getframeinfo(inspect.currentframe().f_back.f_back).filename[0:-3].replace("\\", "/")
        arr = tmp.split('/')
        length = len(arr) - 1
        tmp = f"""{arr[length - 2]}.{arr[length - 1]}.{arr[length]}"""
        self.process = tmp
