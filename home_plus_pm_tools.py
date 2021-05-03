import datetime
import os
import telnetlib
import idt_tools_constant_pm as idtconst
import socket

import idt_tools_file

quarter = (datetime.date.today().month-1)//3 + 1
year = datetime.date.today().year
str_now = datetime.datetime.now().strftime("%Y%m%d_%H%M")
str_log = "LOG_HOMEPLUS_{}".format(str_now)
str_log_quarter = "LOG_{}_Q{}".format(year, quarter)


def pm_execute_homeplus(pm_xlsx_file_name, event_time):
    fail_log_file = os.path.join(os.getcwd(), "HOMEPLUS_PM_Fail_" + event_time + ".log")
    pm_ip_list = idtconst.get_ips_via_excel_homeplus(pm_xlsx_file_name, "IP")
    print("event_time", event_time)
    for ip_idx, ip_info in enumerate(pm_ip_list):
        print(ip_info)
        [device_ip, device_host, device_so, device_type, device_user, device_pw] = ip_info
        str_ip_info = ",".join(ip_info) + "\n"
        try:
            start_time = datetime.datetime.now()
            print(ip_idx, device_ip, device_host, device_so, device_host, device_user, device_pw)
            print(device_ip, "start@", start_time)
            device_cmds = idtconst.get_device_cmds_via_excel_file(device_type, pm_xlsx_file_name)
            if len(device_cmds) > 0:
                work_dir = os.path.join(os.getcwd(), str_log, device_type, device_so)
                if not os.path.exists(work_dir):
                    os.makedirs(work_dir)
                if device_type.upper() == "CGNAT":
                    pass
                    # idtcrtrix.netscaler_log_text(device_ip, device_host, device_so, device_type, device_user,
                    #                              device_pw, device_cmds, event_time)
                elif device_type.upper() == "QB":
                    pass
                    # idtQB.dell_qb_log_and_screens(device_ip, device_host, device_so, device_type, device_user,
                    #                              device_pw, device_cmds, event_time)
                elif device_type.upper() == "N9K":
                    pass
                    # idtssh.pm_ssh_n9k(device_ip, device_host, device_so, device_type, device_user, device_pw,
                    #                         device_cmds, event_time)
                elif device_type.upper() == "CBR8":
                    telnet_ops_command_suite(work_dir, event_time, device_type, device_ip, device_user, device_pw, device_cmds)
                    # telnet_ops_command_suite(device_ip, device_host, device_so, device_type, device_user, device_pw,
                    #                  device_cmds)
                else:
                    telnet_ops_command_suite(device_ip, device_host, device_so, device_type, device_user, device_pw,
                                     device_cmds)
                print("total time of row", ip_idx, (datetime.datetime.now() - start_time).total_seconds())
            else:
                f = open(fail_log_file, "w+")
                print("\n###############################")
                print("Command Sheet %s not found or no command" % device_type)
                print("###############################\n")
                f.write("No Command Sheet," + str_ip_info)
                f.close()
        except socket.timeout:
            f = open(fail_log_file, "w+")
            print("\n###############################")
            print("HOST %s is timeout" % device_host)
            print("###############################\n")
            f.write("socket.timeout," + str_ip_info)
            f.close()
        except OSError:
            f = open(fail_log_file, "w+")
            print("\n###############################")
            print("HOST %s is OSError" % device_host)
            print("###############################\n")
            f.write("OSError," + str_ip_info)
            f.close()
        except:
            f = open(fail_log_file, "w+")
            print("\n###############################")
            print("HOST %s is OSError" % device_host)
            print("###############################\n")
            f.write("UnknownError," + str_ip_info)
            f.close()


def telnet_ops_command_suite(work_dir, event_time, device, ip, pw1, pw2, show_cmds):
    succeeded = True
    try:
        if ip == "N/A":
            print("----telnetinfo-----:----IP 為 N/A 不進行telnet -------", work_dir, event_time, device, ip)
            return [False, ""]
        print("----telnetinfo-----", work_dir, event_time, device, ip, pw1, pw2)
        start_time = datetime.datetime.now()
        print("telnet_so_ops_command_suite @", start_time)
        file_name = device + "(" + ip + ")_" + event_time + ".txt"
        full_file_path = os.path.join(work_dir, file_name)
        telnet = telnetlib.Telnet(ip, port=23, timeout=900)
        print("telneted:", (datetime.datetime.now() - start_time).total_seconds())
        telnet.read_until(b'assword: ', 3)
        print("Password1:", (datetime.datetime.now() - start_time).total_seconds())
        telnet.write(pw1.encode('ascii') + b"\r\n")
        telnet.read_until(b'>', 3)
        telnet.write("enable".encode('ascii') + b"\r\n")
        telnet.read_until(b'assword: ', 3)
        print("Password2:", (datetime.datetime.now() - start_time).total_seconds())
        telnet.write(pw2.encode('ascii') + b"\r\n")
        # terminal length 0: 輸出不停頓(系統會依設定輸出一定行數...然後暫停)
        telnet.write(b"terminal length 0 \r\n")
        telnet.write(b"terminal width 511 \r\n")
        print("start CMD:", (datetime.datetime.now() - start_time).total_seconds())
        if isinstance(show_cmds, dict):
            keys = show_cmds.keys()
            for key in keys:
                # filename = b4af_cmds[key][0], cmd = b4af_cmds[key][1]
                cmd = show_cmds[key][1]
                if len(cmd.strip()) > 0:
                    print("CMD:", cmd)
                    telnet.write(cmd.encode('ascii') + b"\r\n")
        else:
            for cmd in show_cmds:
                cmd = cmd.strip()
                if len(cmd) > 0:
                    if cmd.lower().startswith("show"):
                        print("======executing CMD:", cmd)
                        telnet.write(cmd.encode('ascii') + b"\r\n")
                    else:
                        print("------skipping CMD:", cmd)
        telnet.write(b"exit \r\n")
        print("after CMDs:", (datetime.datetime.now() - start_time).total_seconds())
        # TODO 20200914 也許是這個byte > string 的decode在慢
        print("回傳資料及解碼(ascii > utf8) @", datetime.datetime.now())
        data = telnet.read_all().decode('ascii')
        print(data)
        print("回傳資料及解碼(ascii > utf8) 結束 @", (datetime.datetime.now() - start_time).total_seconds())
        if not os.path.isdir(work_dir):
            os.makedirs(work_dir)
        f = open(full_file_path, "w", encoding="utf-8")
        f.write(data)
        f.close()
        idt_tools_file.txt_remove_blank_line_in_file(full_file_path)
        print("儲存檔案@", full_file_path, (datetime.datetime.now() - start_time).total_seconds())
    except:
        succeeded = False

    return [succeeded, full_file_path]
