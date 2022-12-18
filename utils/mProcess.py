import importlib
import sys
import threading
import time

import window
import traceback
import os

global STOP
STOP = False


def watchdog(pipe):
    while True and not STOP:
        recv = pipe.recv_bytes().decode('utf-8')
        # time.sleep(100)
        if recv == '>exit':
            break
        elif recv == '>alive':
            pipe.send_bytes(f'<|alive|{os.getpid()}'.encode('utf-8'))
    pipe.send_bytes('<done'.encode('utf-8'))


def startProcess(system, package_name, need_import, method, method_, pipe, params=None):
    try:
        global STOP
        thread = threading.Thread(target=watchdog, args=(pipe,))
        thread.setDaemon(True)
        thread.start()
        module = importlib.import_module(package_name)
        if params is None:
            execute = eval(f"""module.Entry({need_import}).{method}()""")
        else:
            execute = eval(f"""module.Entry({need_import}).{method}({params})""")
        if method_.get('return') in ('text', 'json'):
            window.msgbox(execute, 'info')
        else:
            pass
        sys.modules.pop(package_name)
        STOP = True
        thread.join()
    except Exception as e:
        system.logger.error("Module execute failed: {0}".format(e))
        window.msgbox("模块执行过程中出现错误\n错误摘要：" + e.__str__() + "\n技术细节：\n" + traceback.format_exc(), 'error')
