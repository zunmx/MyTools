import os.path
from tkinter import *
import tkinter
import win32api
import win32con
import win32ui
from PIL import Image as pimg
from PIL import ImageTk as itk
import gc
import json
import win32gui
import windnd
import traceback
from xml.dom.minidom import parse
import xml.dom.minidom

global system, mainWindow, listWindow, selector_index, labSelector, list_pms_layout, e_edit, list_pms_current_entry
listWindow = None
system = None
mainWindow = None
width = 564
height = 38
selector_index = 1
labSelector = None
selbox = {}
e_edit = None
list_pms_current_entry = None
list_pms_layout = False
list_pms_content = {}
list_pms_i2p_mapping = {}


def get_icon_bin(path, index):
    icon_temp_l, icon_temp_s = win32gui.ExtractIconEx(path, index)
    useIcon = icon_temp_l[0]
    win32gui.DestroyIcon(icon_temp_s[0])
    hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
    hbmp = win32ui.CreateBitmap()
    hbmp.CreateCompatibleBitmap(hdc, 32, 32)
    hdc = hdc.CreateCompatibleDC()
    hdc.SelectObject(hbmp)
    hdc.DrawIcon((0, 0), useIcon)
    bmpstr = hbmp.GetBitmapBits(True)
    icon_bin = pimg.frombuffer('RGBA', (32, 32), bmpstr, 'raw', 'BGRA', 0, 1)
    return icon_bin


def get_non_exe_icon(path):
    fmt = path[path.rfind("."):]
    if fmt == '.msc':
        DOMTree = xml.dom.minidom.parse(path)
        collection = DOMTree.documentElement
        file = collection.getElementsByTagName('Icon')[0].getAttribute('File') if len(
            collection.getElementsByTagName('Icon')) > 0 else "%SystemRoot%\\system32\\mmc.exe"
        if not os.path.exists(file):
            file = "%SystemRoot%\\system32\\" + os.path.basename(file)
        index = collection.getElementsByTagName('Icon')[0].getAttribute('Index') if len(
            collection.getElementsByTagName('Icon')) > 0 else 0
        file = file.replace("%SystemRoot%\Windows", '%SystemRoot%')
        return file, int(index)

    try:
        ffmt = win32api.RegQueryValue(win32api.RegOpenKey(win32con.HKEY_CLASSES_ROOT, fmt, 0, win32con.KEY_READ), '')
        try:
            exe = win32api.RegQueryValueEx(
                win32api.RegOpenKey(win32con.HKEY_CLASSES_ROOT, ffmt + "\DefaultIcon\\", 0, win32con.KEY_READ), '')
            pth = str(exe[0])
        except Exception as e:
            system.logger.warning(f'{fmt} can not find DefaultIcon, try query shell-open-command')
            exe = win32api.RegQueryValueEx(
                win32api.RegOpenKey(win32con.HKEY_CLASSES_ROOT, ffmt + "\shell\open\command\\", 0, win32con.KEY_READ),
                '')
            pth = str(exe[0]).replace(' "%1"', '').replace(" '%1'", '')

        if pth[len(pth) - 1].isnumeric():
            quotoIndex = pth.rfind(",")
            fp = pth[0:quotoIndex]
            idx = int(pth[quotoIndex + 1:])
        else:
            fp = pth
            idx = 0
        if fp.startswith('"'):
            fp = fp[1:-1]
        return fp, idx
    except Exception as e:
        system.logger.warning(
            f"[!] Developer Warning, could not find icon file. details[format={fmt} --> trace_info{traceback.format_exc()}]")


def list_exit():
    global labSelector, e_edit, list_pms_layout, listWindow
    labSelector = None
    list_pms_layout = False
    listWindow.destroy()
    listWindow.quit()
    system.logger.debug(f"gc finished, collect {gc.collect()}")


def selector():
    global selector_index, labSelector
    if labSelector is None:
        labSelector = Label(listWindow, bg='#40c094')
    if len(selbox) > 0:
        labSelector.place(x=3, y=height + (selector_index - 1) * 34 + selector_index * 2 - 2, width=4,
                          height=36)
    else:
        labSelector.place(x=-1, y=-1, width=0, height=0)
    if list_pms_layout:
        e_edit.delete(0, END)
        if selector_index == len(list_pms_i2p_mapping):
            e_edit.insert(0, json.dumps(list_pms_content))
            e_edit.configure(state='readonly')

        else:
            e_edit.configure(state='normal')
            e_edit.delete(0, END)
            e_edit.insert(0, list_pms_content[list_pms_i2p_mapping[selector_index]])


def select(e, idx):  # 选择事件
    global selector_index
    selector_index = idx
    selector()


def enter(event, pms_pre=False):  # 最终的调用
    global list_pms_layout, e_edit, selector_index
    if selector_index not in selbox:
        return
    cmd = selbox[selector_index]
    if cmd['serial'] is None:
        list_pms_layout = False
        e_edit.configure(state='normal')
        list_exit()
        system.executeCommand(cmd['serial'], cmd['entry'])
        return
    if list_pms_layout:
        e_edit.delete(0, END)
        if selector_index != len(list_pms_i2p_mapping):
            e_edit.insert(0, list_pms_content[list_pms_i2p_mapping[selector_index]])
        else:
            list_pms_layout = False
            e_edit.configure(state='normal')
            list_exit()
            system.executeCommand(cmd['serial'], list_pms_current_entry, json.dumps(list_pms_content))
    elif 'params' not in system.command['methods'][f"""{cmd['serial']}$@${cmd['entry']}"""]:
        list_exit()
        system.executeCommand(cmd['serial'], cmd['entry'])

    else:
        list_pms_layout = True
        make_param(cmd)
        e_edit.delete(0, END)


def make_param(cmd):
    global list_pms_current_entry
    idx = 0
    list_pms_current_entry = cmd['entry']
    tmp = system.command['methods'][f"""{cmd['serial']}$@${cmd['entry']}"""]['params']
    for item in tmp:
        idx += 1
        module = system.command['methods'][f"""{cmd['serial']}$@${cmd['entry']}"""]['description']
        if 'icon' in system.command['methods'][f"""{cmd['serial']}$@${cmd['entry']}"""]:
            icon = system.command['methods'][f"""{cmd['serial']}$@${cmd['entry']}"""]['icon']
        elif 'icon' in system.command['serials'][cmd['serial']]:
            icon = system.command['serials'][cmd['serial']]['icon']
        else:
            icon = os.path.join(system.path['RPath'], 'logo.png')
        icon = os.path.join(system.path['TPath'], icon)

        draw_selbox(idx, cmd['serial'], tmp[item], module, item, icon)
        list_pms_content[item] = ""
        list_pms_i2p_mapping[idx] = item
    idx += 1
    draw_selbox(idx, cmd['serial'], '调用', module, '执行模块', icon)
    list_pms_i2p_mapping[idx] = '$executeCommand$'
    if idx > 0:
        listWindow.geometry(f"{width}x{height + 36 * idx + 6}")
    else:
        listWindow.geometry(f"{width}x{height}")


def draw_selbox(idx, serial, description, module, title, icon):
    selbox[idx] = {'id': idx}
    selbox[idx]['serial'] = serial
    selbox[idx]['entry'] = title
    selbox[idx]['label_title'] = Label(listWindow, text=title, fg='#f0f0f0', font=('微软雅黑', 12, 'bold'),
                                       bg='#1e2225',
                                       anchor=tkinter.W,
                                       cursor='hand2')
    selbox[idx]['label_desc'] = Label(listWindow, text=description, fg='#e0e0e0', font=('微软雅黑', 10),
                                      bg='#1e2225',
                                      anchor=tkinter.W,
                                      cursor='hand2')
    selbox[idx]['label_module'] = Label(listWindow, text=module, fg='#d0d0d0', font=('微软雅黑', 8),
                                        bg='#1e2225',
                                        anchor=tkinter.E,
                                        cursor='hand2')
    if type(icon) == str:
        selbox[idx]['image'] = pimg.open(icon)
        selbox[idx]['image'] = selbox[idx]['image'].resize((32, 32))
        selbox[idx]['img'] = itk.PhotoImage(selbox[idx]['image'])
    else:
        selbox[idx]['image'] = icon
        selbox[idx]['image'] = selbox[idx]['image'].resize((32, 32))
        selbox[idx]['img'] = itk.PhotoImage(selbox[idx]['image'])
    selbox[idx]['label_pic'] = Label(listWindow, text='', image=selbox[idx]['img'], bg='#1e2225', anchor=tkinter.W,
                                     cursor='hand2')
    selbox[idx]['label_pic'].image = selbox[idx]['img']
    selbox[idx]['label_title'].place(x=48, y=height + (idx - 1) * 34 + idx * 2 - 0, width=415,
                                     height=16)
    selbox[idx]['label_desc'].place(x=48, y=height + (idx - 1) * 34 + idx * 2 + 16, width=415,
                                    height=16)

    selbox[idx]['label_module'].place(x=462, y=height + (idx - 1) * 34 + idx * 2, width=102,
                                      height=32)
    selbox[idx]['label_pic'].place(x=11, y=height + (idx - 1) * 34 + idx * 2, width=38,  #
                                   height=32)

    selbox[idx]['label_title'].bind("<Enter>", lambda event, idx=idx: select(event, idx))
    selbox[idx]['label_desc'].bind("<Enter>", lambda event, idx=idx: select(event, idx))
    selbox[idx]['label_module'].bind("<Enter>", lambda event, idx=idx: select(event, idx))
    selbox[idx]['label_pic'].bind("<Enter>", lambda event, idx=idx: select(event, idx))
    selbox[idx]['label_title'].bind("<Button-1>", lambda event, idx=idx: enter(event))
    selbox[idx]['label_desc'].bind("<Button-1>", lambda event, idx=idx: enter(event))
    selbox[idx]['label_module'].bind("<Button-1>", lambda event, idx=idx: enter(event))
    selbox[idx]['label_pic'].bind("<Button-1>", lambda event, idx=idx: enter(event))


def make_list(lists):
    command = system.command
    global selbox
    for index in selbox:
        for item in selbox[index]:
            if item not in ('id', 'serial', 'entry', 'image', 'img'):
                selbox[index][item].destroy()
            else:
                selbox[index][item] = None
    selbox = {}
    idx = 0
    for item in lists:
        title = item
        serial = lists[item]
        if idx == int(system.config['window']['list']['maxItem']): break
        if serial is not None:
            for i in command['serials'][serial]['methods']:
                if i['entry'] == item:
                    idx += 1
                    module = command['serials'][serial]['module']
                    if 'icon' in i:
                        icon = i['icon']
                    else:
                        if 'icon' in command['serials'][serial]:
                            icon = command['serials'][serial]['icon']
                        else:
                            icon = os.path.join(system.path['RPath'], 'logo.png')
                    description = i['description']
                    icon = os.path.join(system.path['TPath'], icon)
                    if not os.path.exists(icon):
                        system.logger.warning('Resource file not exists: %s' % icon)
                        icon = os.path.join(system.path['RPath'], 'logo.png')
                    draw_selbox(idx, serial, description, module, title, icon)
        else:
            for i in command['custom']:
                if i == item:
                    idx += 1
                    module = '自配置启动项'
                    description = command['custom'][i]['path']  # 文件路径
                    if 'icon' in command['custom'][i]:
                        icon = command['custom'][i]['icon']
                    if (not os.path.exists(icon) or icon == "" or icon == "$default$"):
                        if os.path.basename(description).endswith('.exe'):
                            icon = get_icon_bin(description, 0)
                        else:
                            try:
                                a, b = get_non_exe_icon(description)
                                icon = get_icon_bin(a, b)
                            except Exception as e:
                                system.logger.warning(
                                    'ICON get failure, source_path=' + description + f""" - cause by {traceback.format_exc()}""")
                                icon = os.path.join(system.path['RPath'], 'logo.png')
                    draw_selbox(idx, serial, description, module, title, icon)
    if idx > 0:
        listWindow.geometry(f"{width}x{height + 36 * idx + 6}")
    else:
        listWindow.geometry(f"{width}x{height}")


def msgbox(message, types):
    if types == 'info':
        win32api.MessageBox(0, str(message), '提示', win32con.MB_ICONINFORMATION)
    elif types == 'warning':
        win32api.MessageBox(0, str(message), '需要注意', win32con.MB_ICONWARNING)
    elif types == 'error':
        win32api.MessageBox(0, str(message), '出现错误', win32con.MB_ICONERROR)


def create_list_window(event):
    global list_pms_layout, selector_index

    def change(event):
        global list_pms_layout, selector_index
        methods_list = {}
        if event.keycode == 13:
            if list_pms_layout:
                if selector_index == len(list_pms_i2p_mapping):
                    enter(None, True)
                    return
                selector_index += 1
                selector()

            else:
                enter(event)
            # 调用方法
        elif event.keycode == 27:
            list_exit()
        elif event.keycode == 38:
            if selector_index == 1: return
            selector_index -= 1
            selector()
        elif event.keycode == 40:
            if selector_index == len(selbox): return
            selector_index += 1
            selector()
        else:
            if not list_pms_layout:
                command = system.command
                selector_index = 1
                for cmd in command['methods'].keys():
                    tmp = cmd.split("$@$")
                    serial = tmp[0]
                    function = tmp[1]
                    if e_edit.get().lower() in str(function).lower():
                        methods_list[function] = serial
                for cmd in command['custom'].keys():
                    serial = None
                    function = cmd
                    if e_edit.get().lower() in str(function).lower():
                        methods_list[function] = serial
                make_list(methods_list)
                selector()
            else:
                if selector_index != len(list_pms_i2p_mapping):
                    list_pms_content[list_pms_i2p_mapping[selector_index]] = e_edit.get()

    def on_focus_out(event):
        list_exit()

    global listWindow, e_edit
    sX = win32api.GetSystemMetrics(0)  # 获得屏幕分辨率X轴
    sY = win32api.GetSystemMetrics(1)  # 获得屏幕分辨率Y轴
    win = tkinter.Toplevel(mainWindow)
    win.title = 'select_window'
    win.configure(bg="#1e2225")
    win.geometry(f"""+{int(sX / 2 - width / 2)}+{int(sY / 3 - height / 2)}""")
    win.geometry(f'{width}x{height}')

    win.overrideredirect(True)  # 无标题栏窗体
    # 输入框
    e_edit = Entry(win, width=78, font=('微软雅黑', 16, 'bold'), insertwidth=2, bg="#2f3336", fg="#ffffff",
                   insertbackground='#ffffff', borderwidth=0)
    e_edit.place(x=1, y=1,
                 width=width - 39, height=height - 2)
    e_edit.configure(state='normal')
    e_edit.bind("<KeyRelease>", change)
    # 右侧图标
    bg = PhotoImage(file=os.path.join(system.path['RPath'], 'logo.png'))
    la1 = Label(win, image=bg)
    la1.place(x=width - 37, y=1, width=36, height=36)
    # 窗口配置
    win.wm_attributes('-alpha', 0.7)
    # win.bind("<FocusOut>", on_focus_out)
    win.attributes("-topmost", 1)
    e_edit.focus_set()
    listWindow = win
    win.mainloop()


def createWindow(sysmodule):
    global system, mainWindow
    system = sysmodule

    def __drag(files):
        system.append_custom_entry(files)

    def MouseDown(event):  # 不要忘记写参数event
        global mousX  # 全局变量，鼠标在窗体内的x坐标
        global mousY  # 全局变量，鼠标在窗体内的y坐标

        mousX = event.x  # 获取鼠标相对于窗体左上角的X坐标
        mousY = event.y  # 获取鼠标相对于窗左上角体的Y坐标

    def MouseMove(event):
        w1 = la1.winfo_x()  # w1为标签1的左边距
        h1 = la1.winfo_y()  # h1为标签1的上边距
        root.geometry(f'+{event.x_root - mousX - w1}+{event.y_root - mousY - h1}')  # 窗体移动代码

    def MouseUp(event):
        if system.config['window']['position-x'] != root.winfo_x() and system.config['window'][
            'position-y'] != root.winfo_y():
            system.config['window']['position-x'] = root.winfo_x()
            system.config['window']['position-y'] = root.winfo_y()
            system.save_config()

    def exit(event):
        root.destroy()  # 退出程序
        root.quit()

    root = tkinter.Tk()
    root.title('mainWindow')
    root.geometry('48x48')
    root.geometry(f'+{system.config["window"]["position-x"]}+{system.config["window"]["position-y"]}')
    root.overrideredirect(True)  # 无标题栏窗体
    root.attributes("-topmost", 1)
    bg = PhotoImage(file=os.path.join(system.path['RPath'], 'logo.png'))
    la1 = Label(root, text='', image=bg, cursor='heart')
    la1.pack(padx=0, pady=0)
    root.wm_attributes('-alpha', 0.8)
    la1.bind("<Button-1>", MouseDown)  # 按下鼠标左键绑定MouseDown函数
    la1.bind("<ButtonRelease-1>", MouseUp)  # 按下鼠标左键绑定MouseDown函数
    la1.bind("<B1-Motion>", MouseMove)  # 鼠标左键按住拖曳事件
    la1.bind("<Double-Button-1>", create_list_window)
    mainWindow = root
    windnd.hook_dropfiles(mainWindow, __drag)
    root.mainloop()
