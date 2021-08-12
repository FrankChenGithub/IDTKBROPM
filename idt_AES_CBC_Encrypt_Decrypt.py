# todo 說明---
#  1.Web Service網址：【https://idtwebapi-v2.idtech.com.tw//api/Verify?IdInfos=加密參數】。
#  2.Web Service請求類別：【GET】。
#  3.加密參數內容：【帳號(userid)】【密碼(pws)】【應用程式(app)】。
#  Ex(解密後)：{"userid':"randyw","pwd":"xxxxxx","app":"app name"}
#  4.加密回傳內容：【結果代碼(status_code)】【鎖定分鐘數(delay)】。
#  i.結果代碼：
#    -1：驗證失敗超過三次，需等鎖定分鐘數(delay)之後才能再驗證。
#        Ex(解密後)：{" status_code:"-1"," delay ":"15"}
#     0：驗證失敗。
#        Ex(解密後)：{" status_code:"0"," delay ":"0"}
#     1： 驗證成功。
#        Ex(解密後)：{" status_code:" 1"," delay ":"0"}
#  ii.鎖定分鐘數：預設15分鐘，依帳號驗證失敗超過三次開始倒數15分鐘才能再度驗證。
#  Frank@20210222 Crypto 目前使用 pycryptodome 套件，以如下pip指令安裝
#  pip install pycryptodome

import hashlib
import json
from base64 import b64encode, b64decode
import tkinter as tk
import tkinter.font as tkFont
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from urllib import parse
key = '80192260'
idt_security_link = r"https://idtwebapi-v2.idtech.com.tw//api/Verify?IdInfos={}"


class IDTAppAuthentication:
    def __init__(self):
        self.user_id = ""
        self.user_pw = ""
        self.authen_code = -1
        self.authen_delay = 0
        self.authen_time = ""
        self.app_name = ""
        self.proc_name = ""


def encrypt_data(data):
    # 將key用md5雜湊產生key
    m = hashlib.md5()
    m.update(key.encode("utf8"))
    keyBytes = m.digest()
    # AES CBC MODE 加密
    cipher = AES.new(keyBytes, AES.MODE_CBC, keyBytes)  #key ,iv 都用 keyBytes簡化處理
    cipheredData = cipher.encrypt(pad(data.encode("utf8"), AES.block_size)) # 將輸入資料加上 padding 後進行加密
    return parse.quote(b64encode(cipheredData).decode("utf8")) #加上urllib.parse處理特殊符號傳輸異常


def decrypt_data(encodedStr):
    # 將key用md5雜湊產生key
    m = hashlib.md5()
    m.update(key.encode("utf8"))
    keyBytes = m.digest()
    # AES CBC MODE 解密
    cipher = AES.new(keyBytes, AES.MODE_CBC, keyBytes)  #key ,iv 都用 keyBytes簡化處理
    encrypted_bytes = b64decode(parse.unquote(encodedStr).encode('utf-8'))  #加上urllib.unquote處理特殊符號傳輸異常
    originalData = unpad(cipher.decrypt(encrypted_bytes), AES.block_size)
    return originalData.decode("utf8")


def idt_user_authentication(IdInfo):
    # IdInfo = {"userid": "randyw", "pwd": "xxxxxx", "app": "凱播改接輔助工具"}
    authentication_code = 999
    authentication_delay = 0
    IdInfo_string = json.dumps(IdInfo)
    encrypt_str = encrypt_data(IdInfo_string)
    link = idt_security_link.format(encrypt_str)
    resp = requests.get(link)
    if resp.status_code != 200:
        # This means something went wrong.
        print(resp.status_code)
    else:
        # print("resp")
        # print(resp)
        # print("------------------------------------------------------------")
        auth_status = resp.content
        # print(auth_status)
        dec_status = decrypt_data(auth_status)
        # print(dec_status)
        dec_json = json.loads(dec_status)
        # print("status_code:", dec_json["status_code"])
        # print("delay:", dec_json["delay"])
        authentication_code = int(dec_json["status_code"])
        authentication_delay = int(dec_json["delay"])
    return [authentication_code, authentication_delay]


class IDTAthenDialog:
    def __init__(self, parent, app_name, proc_name):
        self.app_name = app_name
        self.proc_name = proc_name
        self.user_id = ""
        self.user_pw = ""
        self.authen_code = -1
        self.authen_delay = 0
        self.pw_error = tk.StringVar()
        top = self.top = tk.Toplevel(parent)
        top.geometry("370x170")
        top.title("idt作業人員認證")
        font_mid = tkFont.Font(family="Helvetica", size=16)
        font_small = tkFont.Font(family="Helvetica", size=12)
        self.myLabel = tk.Label(top, text=r'請輸入你的idt帳密(不需輸入domain)', font=font_mid)
        self.myLabel.place(x=10, y=10)
        self.label_user_id = tk.Label(top, text="帳號:", font=font_mid).place(x=10, y=40)
        self.entry_user_id = tk.Entry(top, state=tk.NORMAL, width=20, font=font_mid)
        self.entry_user_id.place(x=80, y=40)
        self.label_user_pw = tk.Label(top, text="密碼:", font=font_mid).place(x=10, y=80)
        self.entry_user_pw = tk.Entry(top, state=tk.NORMAL, show='*', width=20, font=font_mid)
        # self.entry_user_pw.bind('<Return>', self.send)
        self.entry_user_pw.place(x=80, y=80)
        self.mySubmitButton = tk.Button(top, text='Submit', command=self.send, font=font_mid, bg="yellow")
        self.mySubmitButton.place(x=10, y=120)
        self.label_pw_error = tk.Label(top, textvariable=self.pw_error, font=font_small, fg="red").place(x=100, y=125)

    def send(self):
        # global user_id
        # global user_pw
        self.user_id = self.entry_user_id.get()
        self.user_pw = self.entry_user_pw.get()
        # user_info = {"userid": self.user_id, "pwd": self.user_pw, "app": "凱播改接輔助工具||程式測試"}
        user_info = {"userid": self.user_id, "pwd": self.user_pw, "app": "{}||{}".format(self.app_name, self.proc_name)}
        [auth_code, auth_delay] = idt_user_authentication(user_info)
        self.authen_code = auth_code
        self.authen_delay = auth_delay
        print(self.user_id, auth_code, auth_delay)
        if self.authen_code == 999:
            self.pw_error.set("無法連線idtech，請確認連線")
        elif self.authen_code == 1:
            self.top.destroy()
        else:
            if self.authen_delay == 0:
                self.pw_error.set("帳號輸入錯誤")
            else:
                self.pw_error.set("此帳號密碼錯誤>=3次，須等候{}分鐘".format(self.authen_delay))
