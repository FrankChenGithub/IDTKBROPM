import subprocess


def map_idt_server_folder_to_drive(unc_path, user_domain, user_id, user_pw, drive_letter):
    # todo 先刪除，再建立 (Disconnect anything on drive_letter)
    #  r'net use m: /del'
    #  r'net use m: \\10.0.100.90\73c20-區域\客戶資料 /user:user_domain\user_id user_pw'
    subprocess.call(r'net use {}: /del'.format(drive_letter), shell=True)
    proc_str = r'net use {}: {} /user:{}\{} {}'.format(drive_letter, unc_path, user_domain, user_id, user_pw)
    subprocess.call(proc_str, shell=True)



