# from tkinter import END, Label, Listbox, Frame, Scrollbar
import datetime
import sys
import os
from os import listdir
from os.path import isfile, join
from tkinter import *
import tkinter.font as tkFont
from tkinter import messagebox
from tkinter.ttk import Combobox
import idt_tools_general_pm as idtgen
import idt_tools_constant_pm as idtconst
import KBROPM2021
import idt_AES_CBC_Encrypt_Decrypt as idtauthen
import idt_tools_env_check as idtapenv

title_start = "{}: {} 尚未登入"
title_loginned = "{}: {} (登入為:{}-)"
APP_NAME = "凱擘系統 定保工具"
APP_VERSION = "2021-08-02版"
IDTAPPAUTHEN = idtauthen.IDTAppAuthentication()
IDTAPPAUTHEN.app_name = APP_NAME

debug_mode = False
debug_work_dir = ""
work_dir = os.getcwd()
event_day = datetime.datetime.now().strftime("%Y%m%d")
quarter = (datetime.date.today().month-1)//3 + 1
year = datetime.date.today().year
# str_now = datetime.datetime.now().strftime("%Y%m%d_%H%M")
# str_log = "LOG_{}".format(str_now)
str_log_quarter_temp = "LOG_{}_Q{}"

execution_log = "execution.log"
execution_log_path = ""
folder_log = ""

top = Tk()
bigfont = tkFont.Font(family="Helvetica", size=20)
font_mid = tkFont.Font(family="Helvetica", size=16)
font_small = tkFont.Font(family="Helvetica", size=12)
font_mini = tkFont.Font(family="Helvetica", size=10)
fontStyle20 = tkFont.Font(size=20)

xlsx_ops_sel = StringVar()
xlsx_ops = []
userid = StringVar(value="frankchen")
password = StringVar(value="")
driveid = StringVar(value="M")
copy_pm_to_server = IntVar(value=0)
op_quarter = IntVar(value=quarter)
kbro_pm_xlsx_file_name = 'XLSX_KBRO/KBRO PM.xlsx'
# kbro_pm_xlsx_file_name = "KBRO PM_20201102_FrankKu.xlsx"
# kbro_pm_xlsx_file_name = "KBRO PM_20201102_JOY.xlsx"
# kbro_pm_xlsx_file_name = "KBRO PM_20210125_CGNAT.xlsx"
# kbro_pm_xlsx_file_name = 'KBRO PM_20210201_SSH_N9K.xlsx'
# 傅星霖的多command
# kbro_pm_xlsx_file_name = "KBRO PM-Upstream SNR-All.xlsx"


def check_authentication(proc_name):
    if IDTAPPAUTHEN.authen_code == 1:
        IdInfo = {"userid": IDTAPPAUTHEN.user_id, "pwd": IDTAPPAUTHEN.user_pw,
                  "app": "{}||{}".format(APP_NAME, proc_name)}
        [authen_code, authen_delay] = idtauthen.idt_user_authentication(IdInfo)
        print(APP_NAME, proc_name, authen_code, authen_delay)
        return True
    else:
        inputDialog = idtauthen.IDTAthenDialog(top, APP_NAME, proc_name)
        top.wait_window(inputDialog.top)
        IDTAPPAUTHEN.user_id = inputDialog.user_id
        IDTAPPAUTHEN.user_pw = inputDialog.user_pw
        IDTAPPAUTHEN.authen_code = inputDialog.authen_code
        IDTAPPAUTHEN.authen_delay = inputDialog.authen_delay
        IDTAPPAUTHEN.app_name = inputDialog.app_name
        IDTAPPAUTHEN.proc_name = inputDialog.proc_name
        if IDTAPPAUTHEN.authen_code == 1:
            top.title(title_loginned.format(APP_NAME, APP_VERSION, IDTAPPAUTHEN.user_id))
            return True
        else:
            return False


def process_command_line_args(args):
    global debug_mode
    global debug_work_dir

    for arg_idx, arg in enumerate(args, start=0):
        print(arg_idx, arg)
        if arg == "-debug":
            debug_mode = True
        elif arg == "-wdir":
            debug_work_dir = args[arg_idx+1]


def write_operation(ops):
    file = open(execution_log_path, mode="a+")
    file.write(ops + "\n")
    file.close()


def init():
    global work_dir
    global cbr8_unique_list
    global cbr8_info_list
    global folder_log
    global execution_log_path

    if len(debug_work_dir) > 0:
        work_dir = debug_work_dir

    execution_log_path = os.path.join(folder_log, execution_log)
    find_pm_xlsx_file_list()


def setting_gui():
    top.geometry("600x140")
    top.title('{}({})'.format(APP_NAME, APP_VERSION))
    [x0, y0] = [10, 10]
    Label(top, text="PM XLSX:", font=font_mid).place(x=x0, y=y0)
    pm_xlsx_ops = Combobox(top, state="readonly", width=36, name="ops_chosen", font=font_mid,
                           textvariable=xlsx_ops_sel)
    pm_xlsx_ops.place(x=x0+120, y=y0)
    pm_xlsx_ops['value'] = xlsx_ops
    pm_xlsx_ops.bind("<<ComboboxSelected>>", callback_ops_selected)
    y1 = 50
    Label(top, text="維護季度:", font=font_mid).place(x=10, y=y1)
    # Radiobutton(top, text="Q1", variable=op_quarter, value=1, font=font_small, fg='blue').place(x=x0+20, y=y1)
    y2 = y1 + 30
    Radiobutton(top, text="Q1", variable=op_quarter, value=1, font=font_mid, fg='blue').place(x=x0, y=y2)
    Radiobutton(top, text="Q2", variable=op_quarter, value=2, font=font_mid, fg='blue').place(x=x0 + 80, y=y2)
    Radiobutton(top, text="Q3", variable=op_quarter, value=3, font=font_mid, fg='blue').place(x=x0 + 160, y=y2)
    Radiobutton(top, text="Q4", variable=op_quarter, value=4, font=font_mid, fg='blue').place(x=x0 + 240, y=y2)
    # chk_copy = Checkbutton(top, text="複製定保檔案至伺服器相應目錄", variable=copy_pm_to_server, font=font_mid, fg='blue')
    # chk_copy.place(x=x0, y=y1)
    # y2 = 90
    # Label(top, text="伺服器路徑對應網路磁碟編碼:", font=font_mid).place(x=10, y=y2)
    # Entry(top, state=NORMAL, textvariable=driveid, width=4, font=font_mid).place(x=310, y=y2)
    btn_execute = Button(top, text="執行PM程式", command=callback_execute_pm, font=font_mid, bg='aqua', fg='red')
    btn_execute.place(x=440, y=y1+20)
    top.mainloop()


def callback_ops_selected(event):
    xlsx_file = os.path.join(work_dir, xlsx_ops_sel.get())
    print("callback_ops_selected", xlsx_file)


def check_app_env():
    [status, msg] = idtapenv.check_chromedriver_version("")
    msgs = msg
    if msg != "OK":
        if status == "NOEXE":
            s1 = "請至下列網址下載適合的版本"
            s2 = "解壓縮後，取代chromedriver.exe"
            msgs = "{}\n{}\n{}\n{}\n{}".format(msg, s1, idtapenv.chrome_driver_download_url, s2, idtapenv.chromedriver_loc)
        elif status == "WRONGVERSION":
            s2 = "解壓縮後，取代chromedriver.exe"
            msgs = "{}\n{}\n{}".format(msg, s2, idtapenv.chromedriver_loc)
        messagebox.showerror("Chrome Driver 執行檔或版本問題", msgs)
        return False
    [vpn_ok, msg] = idtapenv.check_gateway_ip_availability()
    if not vpn_ok:
        messagebox.showerror("VPN Connectivity Error", msg + "\n 請確認你的VPN連線沒有問題")
        return False

    return True


def callback_execute_pm():
    proc_name = "季維護"
    copy_pm = copy_pm_to_server.get()
    xlsx_name = xlsx_ops_sel.get()
    if len(xlsx_name) == 0:
        messagebox.showinfo("No PM XLSX Selection Error", "請由下拉選單選取PM XLSX檔案")
        return
    xlsx_file = os.path.join(work_dir, xlsx_name)

    if not check_app_env():
        return

    if copy_pm == 1:
        if check_authentication(proc_name):
            # successfully authenticated with idt
            drive_id = driveid.get()
            unc_path = idtconst.server_log_root_unc_path
            user_domain = idtconst.idt_domain
            idtgen.map_idt_server_folder_to_drive(unc_path, user_domain, IDTAPPAUTHEN.user_id, IDTAPPAUTHEN.user_pw,
                                                  drive_id)
        else:
            return
    str_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    int_op_quarter = op_quarter.get()
    str_op_quarter = "Q{}".format(int_op_quarter)
    str_log_quarter = str_log_quarter_temp.format(year, int_op_quarter)
    print(int_op_quarter, str_op_quarter, str_log_quarter)
    KBROPM2021.pm_execute_ops(xlsx_file, str_time, str_op_quarter)
    KBROPM2021.separate_files_via_ma_local(idtconst.str_log, str_log_quarter)
    # Modify20210511 完成作業後關閉畫面
    top.destroy()


def find_pm_xlsx_file_list():
    # 檢查目錄，如果目錄不存在，是第一次，空的
    if os.path.isdir(work_dir):
        xlsx_files = [f for f in listdir(work_dir) if f[-4:] == "xlsx" and isfile(join(work_dir, f))]
        xlsx_files = sorted(xlsx_files)
        for idx, xlsx_file in enumerate(xlsx_files, start=0):
            xlsx_ops.append(xlsx_file)


print('Number of arguments:', len(sys.argv), 'arguments.')
print('Argument List:', str(sys.argv))
process_command_line_args(sys.argv)
init()
setting_gui()
