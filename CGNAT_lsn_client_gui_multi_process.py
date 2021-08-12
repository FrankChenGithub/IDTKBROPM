import datetime

import paramiko
import os
import tkinter as tk
import tkinter.font as tkFont
from datetime import date
import multiprocessing as mp
import idt_tools_citrix_netscaler as idtssh
import idt_tools_cgnat_lsn as idtcgnatlsn

APP_NAME = "KBRO CGNAT工具"
APP_VERSION = "2021-08-02版"
title_start = "{}: {} 尚未登入"
title_loginned = "{}: {} (登入為:{}-)"


cgnat_ips_dict = {
    "全聯_UC": {"UC_CGNAT1": "10.222.56.24", "UC_CGNAT2": "10.222.56.25"},
    "北桃園_BNT": {"BNT_CGNAT1": "10.222.64.24", "BNT_CGNAT2": "10.222.64.25"},
    "金頻道_KP": {"KP_CGNAT1": "10.222.32.24", "KP_CGNAT2":"10.222.32.25"},
    "永佳樂_YJL": {"YJL_CGNAT1":"192.168.136.24", "YJL_CGNAT2":"192.168.136.25",
                "YJL_CGNAT3":"192.168.136.64", "YJL_CGNAT4":"192.168.136.65"},
    "聯禾_UCT": {"UCT_CGNAT1": "192.168.160.40", "UCT_CGNAT2": "192.168.160.41"},
    "豐盟_FM": {"FM_CGNAT1": "10.222.80.24", "FM_CGNAT2": "10.222.80.25"},
    "新頻道_NCC": {"NCC_CGNAT1": "10.222.88.24", "NCC_CGNAT2": "10.222.88.25"},
    "觀昇_KS": {"KS_CGNAT1": "10.222.104.24", "KS_CGNAT2": "10.222.104.25"},
    "南天_NT": {"NT_CGNAT1": "10.220.96.24", "NT_CGNAT2":"10.220.96.25"},
    "鳳信_PHC": {"PHC_CGNAT1": "192.168.169.24", "PHC_CGNAT2": "192.168.169.25"}
}

cgnat_user = "citrix_pm"
cgnat_pw = "citrix_pm@123"

cmds = ["sh lsn client",
        "show lsn deterministicNat -clientname {CLIENT_NAME}"]

top = tk.Tk()
top.geometry('420x320')
# top.title(title_start)
top.title(title_start.format(APP_NAME, APP_VERSION))

bigfont = tkFont.Font(family="Helvetica", size=20)
font_mid = tkFont.Font(family="Helvetica", size=16)
font_small = tkFont.Font(family="Helvetica", size=12)
lbox_so_name_with_codes = tk.Listbox

work_dir = os.getcwd()


def cgnat_proc_a_device(device_ip, device_host, so_as_key, data_dir, device_user, device_pw, xtime):
    [is_primary, log_file_abs] = idtssh.cgnat_show_lsn_session_worker_check_primary(
        device_ip, device_host, so_as_key, data_dir, device_user, device_pw, xtime)
    if is_primary:
        idtcgnatlsn.cgnat_so_device_log_to_xlsx(log_file_abs, so_as_key, device_host, xtime)


def callback_lsn_client_execute():
    selected_so_indices = lbox_so_name_with_codes.curselection()
    op_so_list = []
    today = date.today().strftime("%Y%m%d")
    for idx in selected_so_indices:
        op_so_list.append(lbox_so_name_with_codes.get(idx))

    if len(op_so_list) > 0:
        for so in op_so_list:
            print(so)
        xxx(cgnat_ips_dict, op_so_list)
    else:
       print("no so selected: do nothing")


def xxx(so_ips_dict, sel_sos):
    device_user = cgnat_user
    device_pw = cgnat_pw
    time_start = datetime.datetime.now()
    xminute = datetime.datetime.now().strftime("%Y%m%d%H%M")
    data_dir = os.path.join(work_dir, xminute)
    print(datetime.datetime.now().strftime("%Y%m%d%H%M"), data_dir)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # 1. a. ssh取得log檔案; b. 建立各SO的XLSX (multiprocessing)
    ssh_procs = []
    for so_as_key in sel_sos:
        # xtime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        host_ip_dict = so_ips_dict[so_as_key]
        for device_host in host_ip_dict.keys():
            device_ip = host_ip_dict[device_host]
            proc = mp.Process(target=cgnat_proc_a_device,
                              args=(device_ip, device_host, so_as_key, data_dir, device_user, device_pw, xminute))
            ssh_procs.append(proc)
            proc.start()

    for proc in ssh_procs:
        proc.join()

    #  2. 將xlsx merge成一個
    xlsx_abs = idtcgnatlsn.cgnat_merge_xlsx(data_dir, xminute)
    time_end = datetime.datetime.now()
    print("start@", time_start)
    print("end@", time_end)
    print("total:", time_end - time_start)
    os.system('start excel.exe "{}"'.format(xlsx_abs))


def gui_setting():
    global lbox_so_name_with_codes
    x1 = 20
    y_list = 40
    tk.Label(top, text="選取作業SO(可多選):", font=font_small, fg='blue').place(x=x1, y=10)
    lbox_so_name_with_codes = tk.Listbox(top, height=10, width=16, selectmode=tk.MULTIPLE, exportselection=0)
    lbox_so_name_with_codes.place(x=x1, y=y_list)
    lbox_so_name_with_codes.config(font=font_mid)

    for so_name_with_code in cgnat_ips_dict.keys():
        lbox_so_name_with_codes.insert(tk.END, so_name_with_code)

    x2 = 240
    btn_select_all = tk.Button(top, text="全選", command=lambda: lbox_so_name_with_codes.select_set(0, "end"),
                               font=font_mid, bg='pale green', fg='blue').place(x=x2, y=y_list)
    btn_selection_clear = tk.Button(top, text="全不選", command=lambda: lbox_so_name_with_codes.selection_clear(0, 'end'),
                                    font=font_mid, bg='pale green', fg='blue').place(x=x2, y=y_list+60)

    btn_sop = tk.Button(top, text="執行LSN Client", command=callback_lsn_client_execute, font=font_mid,
                        bg='pale green', fg='blue').place(x=x2, y=y_list + 120)
    top.mainloop()


if __name__ == "__main__":
    mp.freeze_support()
    gui_setting()


