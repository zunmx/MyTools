import copy
import os
import signal
import threading
import gc
import time
import traceback
import sys
import subprocess
import multiprocess
import win32api
import win32con
import mProcess
import window
import logger
import json
import importlib


class System:
    def __init__(self, args=None):
        self.logger = logger.Logger()
        self.path = dict()
        self.path['SPath'] = os.path.abspath(os.getcwd())
        self.path['RPath'] = os.path.join(self.path.get('SPath'), 'res')
        self.path['CPath'] = os.path.join(self.path.get('SPath'), 'conf')
        self.path['UPath'] = os.path.join(self.path.get('SPath'), 'utils')
        self.path['TPath'] = os.path.join(self.path.get('SPath'), 'tools')
        self.command = {"module": {},
                        "methods": {},
                        "serials": {},
                        "custom": {}}
        self.config = None
        self.processList = {}
        self.init_config()
        self.getCommand()
        if args is not None:
            self.logger.debug("System start by args: %s" % args)
            self.starter(args)

    def p_watchdog(self, pipe, pid, cpipe):
        def __inner_watchdog(cpipe):
            time.sleep(1)
            try:
                if pid in self.processList or not cpipe.close:
                    self.logger.debug(
                        f"watchdog resp time {(time.time_ns() - self.processList[pid]['beat_time']) / 1000000000}")
                    if not self.processList[pid]['process'].is_alive():
                        return
                    if (time.time_ns() - self.processList[pid]['beat_time']) / 1000000000 > 10:
                        self.processList[pid]['STOP'] = True
                        cpipe.send_bytes(b"<end")
                        kill()
                    else:
                        threading.Thread(target=__inner_watchdog, args=(cpipe,)).start()
            except KeyError as ex:
                self.logger.warning(
                    f"watchdog has been closed, because pid not in process list {ex}")
            except Exception as ex:
                self.logger.error("watchdog EXCEPTION" + e.__str__())

        def kill():
            self.processList[pid]['STOP'] = True
            self.processList[pid]['process'].terminate()
            time.sleep(1)
            del self.processList[pid]

        self.logger.debug(
            f"module watchdog start,[pid={pid},serial={self.processList[pid]['serial']},method={self.processList[pid]['method']}]")
        __inner_watchdog(cpipe)
        while True and pid in self.processList:
            try:
                self.processList[pid]['beat_time'] = time.time_ns()
                pipe.send_bytes(b">alive")
                get = str(pipe.recv_bytes().decode("utf-8"))
                if pid in self.processList:
                    self.processList[pid]['resp_time'] = time.time_ns()
                if get.startswith("<"):
                    cmr = get[1:]
                    if cmr == 'done':
                        self.logger.debug(f"process manager removed process {pid}")
                        kill()
                        break
                    elif cmr == 'alive':
                        pass
                    elif cmr == 'reload_config':
                        self.init_config()
                        self.getCommand()
                        self.logger.debug(f"recv reload_config command")
                    elif cmr == 'end':
                        self.logger.warning(f"watchdog found process suspend or process non-response {pid}")
                        window.msgbox("模块未能正常响应，请联系模块开发者\n技术细节：心跳包未能在规定时间内响应\n进程信息  "
                                      f"[pid={pid},serial={self.processList[pid]['serial']},method={self.processList[pid]['method']}]",
                                      "warning")
            except Exception as e:
                if pid not in self.processList:
                    self.logger.warning(
                        f"module watchdog finish [pid={pid}], but non-normal exit, cause by {e}")
                    return
                self.logger.error(
                    f"""Process pipe exception, Process {'is alive, but pipe has been close' if self.processList[pid]['process'].is_alive() else 'non-normal'}
                cause by {e}""")
                if not self.processList[pid]['process'].is_alive():
                    window.msgbox("模块非正常退出，请联系模块开发者", "error")
                else:
                    window.msgbox("模块状态异常，技术细节：\n{e}", "error")
                kill()

            time.sleep(1)
        self.logger.debug(
            f"module watchdog finish [pid={pid}]")

    def __execute_(self, package_name, serial, need_import, method, method_, params=None):
        parent, child = multiprocess.Pipe()
        process = multiprocess.Process(
            target=mProcess.startProcess,
            args=(self, package_name, need_import, method, method_, child, params,))
        process.start()
        self.processList[process.pid] = {'process': process, 'serial': serial, 'method': method, 'STOP': False,
                                         'beat_time': time.time_ns(), 'resp_time': time.time_ns(),
                                         'pipe_p': parent, 'pipe_c': child}
        threading.Thread(target=self.p_watchdog, args=(parent, process.pid, child,)).start()
        process.join()
        if not parent.close: parent.close()
        if not child.close: child.close()
        self.logger.debug(f'subprocess starting [pid={process.pid},package_name={package_name},method={method}]')
        self.logger.debug(f'subprocess end [pid={process.pid},package_name={package_name},method={method}]')
        self.logger.debug(f"gc finished, collect {gc.collect()}")

    def executeCommand(self, serial, method, params=None):
        if serial is None:
            c_method = self.command['custom'][method]
            cwd = os.path.dirname(c_method['path']) if c_method['startPath'] == '$auto$' else c_method[
                'startPath']
            args = c_method['args']
            win32api.ShellExecute(0, 'open', c_method['path'], f'{args}', cwd, 1)
            # subprocess.Popen(c_method['path'] + f" {args}", shell=True, cwd=cwd)
        else:
            try:
                package_name = self.command['serials'][serial].get('package')
                method_ = self.command['methods'][f"""{serial}$@${method}"""]
                need_import = '' if 'import' not in self.command['serials'][serial] else \
                    self.command['serials'][serial][
                        'import']
                self.logger.debug(f'execute method [{method}]')
                threading.Thread(target=self.__execute_,
                                 args=(package_name, serial, need_import, method, method_, params)).start()
                self.logger.debug(f'method [{method}] has been close')
                self.logger.debug(f"gc finished, collect {gc.collect()}")


            except Exception as e:
                self.logger.error("module execute error > " + str(e))
                window.msgbox("方法调用失败\n原因：子模块故障\n技术细节：" + traceback.format_exc(), 'error')

    def getCommand(self):
        self.command = {"module": {},
                        "methods": {},
                        "serials": {},
                        "custom": {}}
        listdir = os.listdir(self.path.get('TPath'))
        for module_file in listdir:
            if not module_file.endswith('.py'):
                continue
            try:
                self.logger.debug(f'Loading modules -->[{module_file}]')
                module = importlib.import_module(f'tools.{module_file.replace(".py", "")}')
                boot = module.Entry().boot()
                boot['package'] = f'tools.{module_file.replace(".py", "")}'
                if boot.get('serial') in self.command.get('serials'):
                    self.logger.error(f'''serial exists by {self.command['module']}''')
                    window.msgbox(f"模块[{module_file}]加载失败，本次不进行加载.\n如果是自行添加的，请检查创作规则。\n错误描述：序列号重复", 'warning')
                    continue
                self.command['module'][boot.get('module')] = boot
                self.command['serials'][boot.get('serial')] = boot
                for method in boot.get('methods'):
                    self.command['methods'][boot.get('serial') + "$@$" + method.get('entry')] = method
                    self.logger.debug(f"""add method [{method.get('entry')}] <--- {module_file}""")
                for executor in self.config['custom']:
                    self.logger.debug(f"""add method [{executor}] from custom""")
                    self.command['custom'][executor] = self.config['custom'][executor]
            except Exception as e:
                window.msgbox(f"模块{module_file}加载失败，本次不进行加载.\n如果是自行添加的，请检查创作规则。", 'error')
                self.logger.error(f'Exception by loading module -->[{module_file}] ' + str(e))

    def init_config(self):
        config_path = os.path.join(self.path['CPath'], 'config.json')
        self.logger.debug(f'init configuration')
        if not os.path.exists(config_path):
            self.logger.error('Error open config, file does not exist: %s' % config_path)
            window.msgbox("尚未发现配置文件", "error")
        try:
            with open(config_path) as f:
                self.config = json.loads(f.read())
        except Exception as e:
            self.logger.error('Error loading config ->' + str(e))
            window.msgbox("      配置文件的JSON解析失败\n具体报错原因:\n" + str(e), "error")

    def save_config(self):
        config_path = os.path.join(self.path['CPath'], 'config.json')
        with open(config_path, 'w') as f:
            f.write(json.dumps(self.config, ensure_ascii=False))
            f.flush()
        self.logger.debug('Persist the configuration file.')

    def starter(self, args):
        # pass
        print(self.command['custom'])
        # self.executeCommand('5c7b953e6de21c0f51a9b9c2884d7bef', 'get_ip')
        # self.executeCommand('5c7b953e6de21c0f51a9b9c2884d7bef', 'get_ip')
        # self.executeCommand('5c7b953e6de21c0f51a9b9c2884d7bef', 'get_ip')
        # self.executeCommand('5c7b953e6de21c0f51a9b9c2884d7bef', 'get_ip')
        # self.executeCommand('5c7b953e6de21c0f51a9b9c2884d7bef', 'get_hosts')
        # self.executeCommand('5c7b953e6de21c0f51a9b9c2884d7bef', 'get_hosts')
        # self.executeCommand('5c7b953e6de21c0f51a9b9c2884d7bef', 'get_hosts')
        # self.executeCommand('5c7b953e6de21c0f51a9b9c2884d7bef', 'get_hosts')
        # self.executeCommand('5c7b953e6de21c0f51a9b9c2884d7bef', 'get_ip')

    def append_custom_entry(self, files):
        for file in files:
            fileName = os.path.basename(file.decode('gbk'))
            filePath = file.decode('gbk')
            if fileName not in self.config['custom']:
                self.logger.debug(f'custom append entry:{fileName}')
                self.config['custom'][fileName] = {
                    "path": filePath,
                    "icon": "$default$",
                    "startPath": "$auto$",
                    "args": ""
                }
            else:
                box = win32api.MessageBox(0, '欲添加的项目名称已经存在，配置信息如下：\n'
                                             f"路径：{self.config['custom'][fileName]['path']}\n"
                                             f"确定要覆盖原有的吗？", '覆盖确认', win32con.MB_YESNO + win32con.MB_ICONQUESTION)
                if box == win32con.IDYES:
                    self.logger.debug(f'custom append entry:{fileName}')
                    self.config['custom'][fileName] = {
                        "path": filePath,
                        "icon": "$default$",
                        "startPath": "$auto$",
                        "args": ""
                    }
        self.save_config()
        self.command['custom'] = self.config['custom']


    def create_window(self):
        window.createWindow(self)

    def exit(self):
        addin = ""
        for pid in self.processList:
            addin += " /PID " + str(pid)
            # self.processList[pid]['process'].terminate()
            # if not self.processList[pid]['pipe_p'].close: self.processList[pid]['pipe_p'].close()
            # if not self.processList[pid]['pipe_c'].close: self.processList[pid]['pipe_c'].close()

        addin += f' /pid {os.getppid()} /pid {os.getpid()}'
        os.system(f'''taskkill /f  {addin}''')
