import paramiko
import os


def netscaler_show_lsn_client(device_ip, device_user, device_pw):
    if device_user == "" and device_pw == "":
        print("FRANK no row_id, row_pw used default")
        device_user = "citrix_pm"
        device_pw = "citrix_pm@123"

    folder = os.path.join(os.getcwd(), "CGNAT_CLIENT_LOG/%s/" % (device_ip))
    log_file_name = "LSN_{}.csv"
    if not os.path.exists(folder):
        os.makedirs(folder)

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

    ssh.close()

cgnat_ips = [
    "10.220.96.24",
    "192.168.169.24",
    "10.222.56.24",
    "10.222.88.25",
    "10.222.64.24",
    "10.222.104.25",
    "192.168.160.40",
    "10.222.32.24",
    "192.168.136.24",
    "10.222.80.24"
]


cmds = ["sh lsn client",
        "show lsn deterministicNat -clientname {CLIENT_NAME}"]


for cgnat_ip in cgnat_ips:
    print(cgnat_ip)
    netscaler_show_lsn_client(cgnat_ip, "citrix_pm", "citrix_pm@123")

