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
APP_VERSION = "2021-07-30版"
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
top.geometry('280x400')
top.title(title_start)

bigfont = tkFont.Font(family="Helvetica", size=20)
font_mid = tkFont.Font(family="Helvetica", size=16)
font_small = tkFont.Font(family="Helvetica", size=12)
lbox_cgnat_ips = tk.Listbox

work_dir = os.getcwd()


def cgnat_proc_a_device(device_ip, device_host, so_as_key, data_dir, device_user, device_pw, xtime):
    [is_primary, log_file_abs] = idtssh.cgnat_show_lsn_session_worker_check_primary(
        device_ip, device_host, so_as_key, data_dir, device_user, device_pw, xtime)
    if is_primary:
        idtcgnatlsn.cgnat_so_device_log_to_xlsx(log_file_abs, so_as_key, device_host, xtime)


def callback_lsn_client_ips():
    selected_cngat_indices = lbox_cgnat_ips.curselection()
    selected_ips = []
    today = date.today().strftime("%Y%m%d")
    for idx in selected_cngat_indices:
        selected_ips.append(lbox_cgnat_ips.get(idx))
    for so in selected_ips:
        print(so)

    xxx(cgnat_ips_dict, selected_ips)


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
    global lbox_cgnat_ips
    x1 = 20
    y_list = 10
    tk.Label(top, text="選取作業IP:", font=font_small, fg='blue').place(x=x1, y=y_list)
    lbox_cgnat_ips = tk.Listbox(top, height=10, width=20, selectmode=tk.MULTIPLE, exportselection=0)
    lbox_cgnat_ips.place(x=x1, y=y_list+30)
    lbox_cgnat_ips.config(font=font_mid)

    for so_name_with_code in cgnat_ips_dict.keys():
        lbox_cgnat_ips.insert(tk.END, so_name_with_code)

    y_list_cmd = y_list + 290
    btn_select_all = tk.Button(top, text="全選", command=lambda: lbox_cgnat_ips.select_set(0, "end"),
                               font=font_mid, bg='pale green', fg='blue').place(x=x1, y=y_list_cmd)
    btn_selection_clear = tk.Button(top, text="全不選", command=lambda: lbox_cgnat_ips.selection_clear(0, 'end'),
                                    font=font_mid, bg='pale green', fg='blue').place(x=x1+80, y=y_list_cmd)

    btn_sop = tk.Button(top, text="執行LSN Client", command=callback_lsn_client_ips, font=font_mid,
                        bg='pale green', fg='blue').place(x=x1, y=y_list_cmd+50)
    top.mainloop()


if __name__ == "__main__":
    mp.freeze_support()
    gui_setting()



# def netscaler_show_lsn_client(device_ip, device_user, device_pw, device_so, today):
#     if device_user == "" and device_pw == "":
#         print("FRANK no row_id, row_pw used default")
#         device_user = "citrix_pm"
#         device_pw = "citrix_pm@123"
#
#     folder = os.path.join(os.getcwd(), "CGNAT_CLIENT_LOG/{}/".format(device_ip))
#     if not os.path.exists(folder):
#         os.makedirs(folder)
#     log_file_name = "LSN_{}.csv"
#     cgnat_site_csv_name = "{}_cgnat_mapping-{}.csv"
#     sep_idx = device_ip.find("_")
#     if sep_idx > -1:
#         [device_so, device_ip] = device_ip.split("_")
#     print(device_ip, device_so, today)
#
#     cgnat_site_csv = cgnat_site_csv_name.format(device_so, today)
#     cgnat_csv_full = os.path.join(folder, cgnat_site_csv)
#     ssh = paramiko.SSHClient()
#     ssh.load_system_host_keys()
#     ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#     ssh.connect(device_ip,
#                 username=device_user,
#                 password=device_pw,
#                 look_for_keys=False)
#     timeout = 7200
#     cmd1 = "sh lsn client"
#     cmd2 = "show lsn deterministicNat -clientname {}"
#     ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd1)
#     clients = ssh_stdout.readlines()
#     print(clients)
#     for client in clients:
#         client_info = client.split()
#         if len(client_info) > 1:
#             cmd_nat = cmd2.format(client_info[-1])
#             ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd_nat)
#             client_nats = ssh_stdout.readlines()
#             client_csv = log_file_name.format(client_info[-1])
#             client_csv_full = os.path.join(folder, client_csv)
#             with open(client_csv_full, mode="a") as client_csv_file:
#                 client_csv_file.writelines(client_nats)
#             with open(cgnat_csv_full, mode="a") as cgnat_csv_file:
#                 for line in client_nats:
#                     ss = line.strip().split()
#                     if len(ss) == 6:
#                         del ss[0]
#                         cgnat_csv_file.write(",".join(ss)+"\n")
#
#     ssh.close()