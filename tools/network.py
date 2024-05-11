import requests
import os
import webbrowser


class Entry:
    def boot(self):
        app = {"module": "网络相关模块",  # 模块名称
               "description": "提供网络相关服务",  # 模块描述
               "version": 1.0,  # 模块版本
               "icon": "imgs\\net.png",  # 模块默认图标
               "author": "zunmx",  # 模块作者
               "email": "admin@zunmx.top",  # 电子邮箱
               "serial": "5c7b953e6de21c0f51a9b9c2884d7bef",  # 模块序列号，所有模块的序列号都是唯一的
               "methods": [
                   {
                       "entry": "get_ip",  # 方法入口名称， 在这个类中需要存在这个方法
                       "description": "获取本机IP地址列表",  # 方法描述
                       "icon": "imgs\\ip.png",  # 方法图标
                       "return": "json"  # 方法返回值
                   },
                   {
                       "entry": "get_hosts",
                       "description": "获取本机Hosts",
                       "icon": "imgs\\hosts.png",
                       "return": "text"
                   },
                   {
                       "entry": "bd",
                       "description": "百度搜索",
                       "icon": "imgs\\baidu.png",
                       "params": {  # 如果需要二级菜单，就有这项
                           "key": "待搜索的关键字"  # key是菜单名，后面的是描述
                       },
                       "return": "none"
                   },
                   {
                       "entry": "bing",
                       "description": "必应搜索",
                       "icon": "imgs\\bing.png",
                       "params": {
                           "key": "待搜索的关键字"
                       },
                       "return": "none"
                   }
               ]}
        return app

    def __init__(self):
        pass

    def get_ip(self):
        get = requests.get("https://www.zunmx.top/api/single/getIP.php")
        return get.text

    def get_hosts(self):
        with open(os.getenv("windir") + r"\system32\drivers\etc\hosts", 'r', encoding='utf8') as f:
            return f.read()

    def bd(self, params):
        webbrowser.open(f"https://www.baidu.com/s?wd={params['key']}")

    def bing(self, params):
        webbrowser.open(f"https://cn.bing.com/search?q={params['key']}")
