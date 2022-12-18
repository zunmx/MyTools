import base64
import urllib.parse
import json
from Crypto.Cipher import PKCS1_v1_5 as PKCS1_cipher
from Crypto.PublicKey import RSA
from Crypto import Random
import hashlib
import tkinter as ttk


class Entry:
    def __init__(self):
        self.pubkey = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCjAMflsWyhhm0wzpwDft52VA71
uf0ma7/IM2AKRz7CEaAmQgsIK3xtf/teNU0IYkNU2/H2kQbaoiDFNyOEZE57ymD0
IP9rljoTxUbG8HmCLmsw5Fmmh1RUMkq9BxSJMdosqdJwZE1B16XIJGSK+QcCP/1W
f4pQxLy+REAtsNj1rQIDAQAB
-----END PUBLIC KEY-----"""
        self.privkey = """-----BEGIN RSA PRIVATE KEY-----
MIICXQIBAAKBgQCjAMflsWyhhm0wzpwDft52VA71uf0ma7/IM2AKRz7CEaAmQgsI
K3xtf/teNU0IYkNU2/H2kQbaoiDFNyOEZE57ymD0IP9rljoTxUbG8HmCLmsw5Fmm
h1RUMkq9BxSJMdosqdJwZE1B16XIJGSK+QcCP/1Wf4pQxLy+REAtsNj1rQIDAQAB
AoGABudg0A/ydanrpIJPtc8xDWp0gsBYokC0i/5vDihj1lToR06LSJKM79dYlm4j
/9unlefF6QdN9sMgp7G06aXU9BRuof8L9cjJz1bMKhjpF3mmKpEk0pbjgzDBr4OH
PZYJ2lLI6mKhFnUOD+HXbozF78UhgPgg3cwrKxEH8QliTWkCQQDbN74w19aXJiNv
FHpEJMMRYhF1o+4DH1GpVAt2FNXG2hYQ4SMjlBL3U1tFama67QXGt239sNRUwB3c
9ZrYeYO5AkEAvlplw7R/diJ51nYYpmk7RnqQxjiAK0pgVBUsQVBjo37GdlXWQJxO
18oG4GCvcNnQqNZNzodXZ6qdY0Fv1oUjlQJAHdjSGV5ZxkyYCHi2SO7kbEp47BZ8
wooSGUbrJJGjpaZt2LB+k0qG5ou/4oyhHhRFdA/nduILltptdncuNQkeaQJBAJBw
RaHf14wLkwnh6Mh1Ny4+mJZgjxjKQhfrTP5ugnywGOX4MjAqq0TgnqEpnFZ0YPmM
S9P4LKGT/AMxxywvMJUCQQCMEvlk3hULDyYglomaSNN9GHlWxgpDhLVEdsncTzkM
yc843XGA6QMWX6Q8Xb367NvwwL54fsr7grLYedC+Eypd
-----END RSA PRIVATE KEY-----"""

    def boot(self):
        app = {"module": "RSA 加密解密模块",  # 模块名称
               "description": "RSA 加密解密模块",  # 模块描述
               "version": 1.0,  # 模块版本
               "icon": "imgs\\encrypted.png",  # 模块默认图标
               "author": "zunmx",  # 模块作者
               "serial": "0402d2f8ab47d3ea9420cabada6313c9",  # 模块序列号，所有模块的序列号都是唯一的
               "methods": [
                   {
                       "entry": "rsa",  # 方法入口名称， 在这个类中需要存在这个方法
                       "description": "rsa 加密解密模块",  # 方法描述
                       "icon": "imgs\\encrypted.png",  # 方法图标
                       "return": "none"  # 方法返回值
                   }
               ]}
        return app

    def rsa(self):
        # 非对称RSA加密
        def encrypt(data, public_key=self.pubkey):
            if type(data) is str:
                data = data.encode('utf-8')
            pub_key = RSA.importKey(public_key)
            cipher = PKCS1_cipher.PKCS115_Cipher(pub_key, Random.get_random_bytes)
            keyLen = ((int(len(public_key) / 8)) - 11)
            if len(data) <= keyLen:
                rsa_text = base64.b64encode(cipher.encrypt(data))
                return rsa_text
            else:
                start = 0
                encrypt_data = b''
                while start < len(data.decode('utf8')):
                    end = start + keyLen
                    data1 = data.decode('utf8')[start:end]
                    encrypt_data += cipher.encrypt(data1.encode('utf8'))
                    start = start + keyLen
                return base64.b64encode(encrypt_data)

        # 非对称RSA解密
        def decrypt(data, private_key=self.privkey):
            if type(data) is str:
                data = data.encode('utf-8')
            pri_key = RSA.importKey(private_key)
            cipher = PKCS1_cipher.PKCS115_Cipher(pri_key, Random.get_random_bytes)
            binSec = base64.b64decode(data)
            keyLen = pri_key.size_in_bytes()
            if len(data) <= keyLen:
                rsa_text = cipher.decrypt(binSec, 0)
                return rsa_text
            else:
                start = 0
                decrypt_data = b''
                while start < len(binSec):
                    end = start + keyLen
                    data1 = binSec[start:end]
                    decrypt_data += cipher.decrypt(data1, 0)
                    start = start + keyLen
                return decrypt_data.decode('utf-8')

        def jiami():
            self.text3.delete('1.0', 'end')
            self.text3.insert('insert', encrypt(self.text4.get('1.0', 'end'), self.text1.get('1.0', 'end')))

        def on_closing():
            self.root.destroy()
            self.root.quit()

        def jiemi():
            self.text4.delete('1.0', 'end')
            decry = decrypt(self.text3.get('1.0', 'end'), self.text2.get('1.0', 'end'))
            unquote = urllib.parse.unquote(decry)
            try:
                json_dumps = json.dumps(json.loads(unquote), sort_keys=True, indent=4, separators=(',', ': '),
                                        ensure_ascii=False)
                self.text4.insert('insert', json_dumps)
            except Exception as e:
                self.text4.insert('insert', unquote)

        self.root = ttk.Tk()
        self.root.title('ZunMX - Crypto RSA')
        self.root.geometry('990x480')
        self.root.resizable(width=False, height=False)
        ttk.Label(self.root, text="公钥").grid(row=1, column=1)
        self.text1 = ttk.Text(self.root, width=70, height=15)
        self.text1.insert('insert', self.pubkey)
        self.text1.grid(row=2, column=1)
        ttk.Label(self.root, text="私钥").grid(row=1, column=2)
        self.text2 = ttk.Text(self.root, width=70, height=15)
        self.text2.insert('insert', self.privkey)
        self.text2.grid(row=2, column=2)

        ttk.Label(self.root, text="密文（如需解密，写在这里）").grid(row=3, column=1)
        self.text3 = ttk.Text(self.root, width=70, height=15)
        self.text3.grid(row=4, column=1)
        ttk.Label(self.root, text="明文（如需加密，写在这里）").grid(row=3, column=2)
        self.text4 = ttk.Text(self.root, width=70, height=15)
        self.text4.grid(row=4, column=2)

        self.b1 = ttk.Button(self.root, text="解密", width=50, command=jiemi)
        self.b2 = ttk.Button(self.root, text="加密", width=50, command=jiami)

        self.b1.grid(row=5, column=2)
        self.b2.grid(row=5, column=1)
        self.root.protocol("WM_DELETE_WINDOW", on_closing)
        self.root.mainloop()
