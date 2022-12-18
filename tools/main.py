import os
import win32api
import win32con


class Entry:
    def boot(self):
        app = {"module": "myTools 系统模块",  # 模块名称
               "description": "程序操作",  # 模块描述
               "version": 1.0,  # 模块版本
               "author": "zunmx",  # 模块作者
               "import": "pipe, system",  # 需要导入的system模块，这个参数不是必须的
               "serial": "ef6787ca66a799997775c7dfaae8ff74",  # 模块序列号，所有模块的序列号都是唯一的
               "email": "admin@zunmx.top",
               "methods": [
                   {
                       "entry": "exit",  # 方法入口名称， 在这个类中需要存在这个方法
                       "description": "退出程序",  # 方法描述
                   },
                   {
                       "entry": "reload",  # 方法入口名称， 在这个类中需要存在这个方法
                       "description": "重新加载程序",  # 方法描述
                   },
                   {
                       "entry": "reboot",  # 方法入口名称， 在这个类中需要存在这个方法
                       "description": "重新启动电脑",  # 方法描述
                   },
                   {
                       "entry": "shutdown",  # 方法入口名称， 在这个类中需要存在这个方法
                       "description": "关闭计算机",  # 方法描述
                   }
               ]}
        return app

    def __init__(self, pipe=None, system=None):
        if system is not None:
            self.system = system
            self.logger = self.system.logger
            self.pipe = pipe

    def exit(self):
        self.system.exit()

    def reload(self):
        self.pipe.send_bytes(b'<reload_config')
        self.logger.debug("pub reload system")

    def reboot(self):
        box = win32api.MessageBox(0, '你真的要重启电脑吗？', '系统重启确认', win32con.MB_YESNO + win32con.MB_ICONQUESTION)
        if box == win32con.IDYES:
            os.system("shutdown /r /t 15 /c 'myTools执行用户重启命令，15秒后重启计算机'")
            self.logger.info("just reboot system")
        else:
            self.logger.info("cancel reboot system")

    def shutdown(self):
        box = win32api.MessageBox(0, '你真的要关闭脑吗？', '系统关闭确认', win32con.MB_YESNO + win32con.MB_ICONQUESTION)
        if box == win32con.IDYES:
            os.system("shutdown /s /t 15 /c 'myTools执行用户关机命令，15秒后关闭计算机'")
            self.logger.info("just shutdown system")
        else:
            self.logger.info("cancel shutdown system")
