import paramiko
import os
import tkinter as tk
import tkinter.font as tkFont
from datetime import date

title_start = "CGNAT LSN CLIENT工具"
cgnat_ips = sorted(
    [
        "NT_10.220.96.24",
        "PHC_192.168.169.24",
        "UC_10.222.56.24",
        "NCC_10.222.88.25",
        "BNT_10.222.64.24",
        "KS_10.222.104.25",
        "UCT_192.168.160.40",
        "KP_10.222.32.24",
        "YJL_192.168.136.24",
        "FM_10.222.80.24"
    ]
)

cmds = ["sh lsn client",
        "show lsn deterministicNat -clientname {CLIENT_NAME}"]

top = tk.Tk()
top.geometry('280x400')
top.title(title_start)

bigfont = tkFont.Font(family="Helvetica", size=20)
font_mid = tkFont.Font(family="Helvetica", size=16)
font_small = tkFont.Font(family="Helvetica", size=12)
lbox_so_name_with_codes = tk.Listbox


def callback_lsn_client_ips():
    selected_asr_indices = lbox_so_name_with_codes.curselection()
    selected_ips = []
    today = date.today().strftime("%Y%m%d")
    for idx in selected_asr_indices:
        selected_ips.append(lbox_so_name_with_codes.get(idx))
    for cgnat_ip in selected_ips:
        print("execute telnet on ip@", cgnat_ip)
        netscaler_show_lsn_client(cgnat_ip, "citrix_pm", "citrix_pm@123", "", today)
    print("---------------------程式執行完畢---------------")


def netscaler_show_lsn_client(device_ip, device_user, device_pw, device_so, today):
    if device_user == "" and device_pw == "":
        print("FRANK no row_id, row_pw used default")
        device_user = "citrix_pm"
        device_pw = "citrix_pm@123"

    folder = os.path.join(os.getcwd(), "CGNAT_CLIENT_LOG/{}/".format(device_ip))
    if not os.path.exists(folder):
        os.makedirs(folder)
    log_file_name = "LSN_{}.csv"
    cgnat_site_csv_name = "{}_cgnat_mapping-{}.csv"
    sep_idx = device_ip.find("_")
    if sep_idx > -1:
        [device_so, device_ip] = device_ip.split("_")
    print(device_ip, device_so, today)

    cgnat_site_csv = cgnat_site_csv_name.format(device_so, today)
    cgnat_csv_full = os.path.join(folder, cgnat_site_csv)
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(device_ip,
                username=device_user,
                password=device_pw,
                look_for_keys=False)
    timeout = 7200
    cmd1 = "sh lsn client"
    cmd2 = "show lsn deterministicNat -clientname {}"
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd1)
    clients = ssh_stdout.readlines()
    print(clients)
    for client in clients:
        client_info = client.split()
        if len(client_info) > 1:
            cmd_nat = cmd2.format(client_info[-1])
            ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd_nat)
            client_nats = ssh_stdout.readlines()
            client_csv = log_file_name.format(client_info[-1])
            client_csv_full = os.path.join(folder, client_csv)
            with open(client_csv_full, mode="a") as client_csv_file:
                client_csv_file.writelines(client_nats)
            with open(cgnat_csv_full, mode="a") as cgnat_csv_file:
                for line in client_nats:
                    ss = line.strip().split()
                    if len(ss) == 6:
                        del ss[0]
                        cgnat_csv_file.write(",".join(ss)+"\n")

    ssh.close()


def gui_setting():
    global lbox_so_name_with_codes
    x1 = 20
    y_list = 10
    tk.Label(top, text="選取作業IP:", font=font_small, fg='blue').place(x=x1, y=y_list)
    lbox_cgnat_ips = tk.Listbox(top, height=10, width=20, selectmode=tk.MULTIPLE, exportselection=0)
    lbox_cgnat_ips.place(x=x1, y=y_list+30)
    lbox_cgnat_ips.config(font=font_mid)

    for ip in cgnat_ips:
        lbox_cgnat_ips.insert(tk.END, ip)

    y_list_cmd = y_list + 290
    btn_select_all = tk.Button(top, text="全選", command=lambda: lbox_cgnat_ips.select_set(0, "end"),
                               font=font_mid, bg='pale green', fg='blue').place(x=x1, y=y_list_cmd)
    btn_selection_clear = tk.Button(top, text="全不選", command=lambda: lbox_cgnat_ips.selection_clear(0, 'end'),
                                    font=font_mid, bg='pale green', fg='blue').place(x=x1+80, y=y_list_cmd)

    btn_sop = tk.Button(top, text="執行LSN Client", command=callback_lsn_client_ips, font=font_mid,
                        bg='pale green', fg='blue').place(x=x1, y=y_list_cmd+50)
    top.mainloop()


if __name__ == "__main__":
    # print('Number of arguments:', len(sys.argv), 'arguments.')
    # print('Argument List:', str(sys.argv))
    gui_setting()

