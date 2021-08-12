import os
import shutil

import paramiko
import idt_tools_constant_pm as idtconst
import idt_tools_pdf

# citrix_dont_write_cmds = ["vtysh", "ter le 0", "exit", "shell"]
# n9k_dont_write_cmds = ["ter le 0", "ter len 0", "ter wi 511"]


def pm_ssh_n9k(device_ip, device_host, device_so, device_type, device_user, device_pw, cmds, xtime):
    # 1. cmds > a txt
    cmdX = idtconst.n9k_dont_write_cmds
    [log_dir, txt_file_name] = ssh_n9k_to_txt_file(device_ip, device_host, device_so, device_type, device_user, device_pw, cmds, xtime, cmdX)
    # 2. a txt > a pdf
    pdf_file_name = txt_file_name[:-4] + ".pdf"
    pm_convert_txt_to_pdf(log_dir, txt_file_name, pdf_file_name)


def pm_convert_txt_to_pdf(work_dir, txt_file_name, pdf_file_name):
    # FOLDER: LOG/豐盟/ASR/
    # filename: PDF is FOX1729GWHJ_FM-I-ASR-02.pdf
    print("filename PDF is %s" % pdf_file_name)
    pdf_full_path = os.path.join(work_dir, pdf_file_name)
    if os.path.isfile(pdf_full_path):
        os.remove(pdf_full_path)
    temp_pdf_folder = os.path.join(work_dir, "pdf_temp_" + pdf_file_name[:-4])
    idt_tools_pdf.txt_file_to_command_first_page_pdf(work_dir, txt_file_name, temp_pdf_folder, pdf_file_name)
    if os.path.exists(temp_pdf_folder):
        shutil.rmtree(temp_pdf_folder)


def ssh_n9k_to_txt_file(device_ip, device_host, device_so, device_type, device_user, device_pw, cmds, xtime, cmdX):
    if device_user == "" and device_pw == "":
        print("idt pm 無 row_id, row_pw used default")
        device_user = idtconst.pm_user
        device_pw = idtconst.pm_pw

    # folder = os.path.join(os.getcwd(), "LOG/%s/%s/" % (device_so, device_type))
    folder = os.path.join(os.getcwd(), os.path.join("OTHERS/LOG_b4_20210222", os.path.join(device_so, device_type)))
    txt_file_name = "{}_{}_{}.txt".format(device_ip, xtime, device_host)
    txtfile_full_path = os.path.join(folder, txt_file_name)
    if not os.path.exists(folder):
        os.makedirs(folder)
    print(cmds)
    print(txtfile_full_path)
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(device_ip,
                username=device_user,
                password=device_pw,
                look_for_keys=False)

    for cmd_idx, cmd in enumerate(cmds):
        print(cmd_idx, cmd)
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)
        if cmd in cmdX:
            pass
        else:
            data = ssh_stdout.readlines()
            data = ["#" + cmd + "\n"] + data
            if "Error: AAA" in data[-1]:
                del data[-1]
            print(data)
            ssh_append_output_to_txt_file(folder, txtfile_full_path, data)
    ssh.close()
    return [folder, txt_file_name]


def ssh_append_output_to_txt_file(work_dir, txtfile_full_path, data):
    if not os.path.isdir(work_dir):
        os.makedirs(work_dir)
    f = open(txtfile_full_path, "a+")
    f.writelines(data)
    f.close()
    # idt_tools_file.txt_remove_blank_line_in_file(txtfile_full_path)