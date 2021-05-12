############################################################
# import the execl file include the login information
############################################################
import datetime
import os
import shutil
import socket
import idt_tools_constant_pm as idtconst
import idt_tools_pm as idtpm
import idt_tools_citrix_netscaler as idtcrtrix
import idt_tools_QB as idtQB
import idt_tools_ssh as idtssh
import idt_tools_constant_pm as pmconst


def pm_execute_ops(pm_xlsx_file_name, event_time, str_op_quarter):
    fail_log_file = os.path.join(os.getcwd(), "KBRO_PM_Fail_" + event_time + ".log")
    pm_ip_list = idtconst.get_ips_via_excel_file(pm_xlsx_file_name, "IP")
    print("event_time", event_time)
    for ip_idx, ip_info in enumerate(pm_ip_list):
        print(ip_info)
        [device_ip, device_host, device_so, device_type, device_user, device_pw] = ip_info
        str_ip_info = ",".join(ip_info) + "\n"
        try:
            if device_type.upper() == "PNR":
                idtpm.get_pnr_http_screenshot(device_ip, device_host, device_so, device_host, device_user, device_pw)
            else:
                start_time = datetime.datetime.now()
                print(ip_idx, device_ip, device_host, device_so, device_host, device_user, device_pw)
                print(device_ip, "start@", start_time)
                if device_type.upper() == "CGNATLSN":
                    idtcrtrix.netscaler_show_lsn_session_worker(device_ip, device_host, device_so, device_type,
                                                         device_user, device_pw, event_time)
                else:
                    device_cmds = idtconst.get_device_cmds_via_excel_file(device_type, pm_xlsx_file_name, str_op_quarter)
                    for cmd, cmd_idx in enumerate(device_cmds):
                        print(cmd, cmd_idx)

                    if len(device_cmds) > 0 or device_type == "RFGW":
                        if device_type.upper() == "CGNAT":
                            idtcrtrix.cgnat_log_text(device_ip, device_host, device_so, device_type, device_user,
                                                         device_pw, device_cmds, event_time)
                        elif device_type.upper() == "QB":
                            idtQB.dell_qb_log_and_screens(device_ip, device_host, device_so, device_type, device_user,
                                                         device_pw, device_cmds, event_time)
                        elif device_type.upper() == "N9K":
                            idtssh.pm_ssh_n9k(device_ip, device_host, device_so, device_type, device_user, device_pw,
                                                    device_cmds, event_time)
                        else:
                            idtpm.telNetCall(device_ip, device_host, device_so, device_type, device_user, device_pw,
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


def idt_copytree(src, dst):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            if not os.path.exists(d):
                print("creating directory:", d)
                os.makedirs(d)
            print("copy tree:", s, d)
            idt_copytree(s, d)
        else:
            shutil.copy(s, d)


def separate_files_via_ma_local(from_root, to_root):
    kbro_so_dict = pmconst.kbro_so_dict
    print(from_root)
    print(to_root)
    devices = os.listdir(from_root)
    for device in devices:
        # print(device)
        if device.upper() in ("ASR", "CGNAT"):
            source_root = os.path.join(from_root, device)
            to_folder_name = "ASRN9K" if device.upper() == "ASR" else device.upper()
            target_root = os.path.join(to_root, to_folder_name)
            print(source_root, target_root)
            so_names = os.listdir(source_root)
            for a_so_name in so_names:
                so_index = kbro_so_dict[a_so_name]
                src = os.path.join(source_root, a_so_name)
                dst = os.path.join(target_root, so_index, device)
                if not os.path.exists(dst):
                    os.makedirs(dst)
                # todo actual copy from a folder to another
                idt_copytree(src, dst)
        elif device.upper() in ("QB",):
            source_root = os.path.join(from_root, device)
            target_root = os.path.join(to_root, "QB")
            print(source_root, target_root)
            so_names = os.listdir(source_root)
            for a_so_name in so_names:
                src = os.path.join(source_root, a_so_name)
                dst = os.path.join(target_root, a_so_name)
                if not os.path.exists(dst):
                    os.makedirs(dst)
                # todo actual copy from a folder to another
                idt_copytree(src, dst)
        elif device.upper() in ("CBR8", "DTI", "RFGW", "UBR10K"):
            source_root = os.path.join(from_root, device)
            target_root = os.path.join(to_root, "CMTS")
            print(source_root, target_root)
            so_with_branches = os.listdir(source_root)
            for a_branch in so_with_branches:
                leftp = a_branch.find("(")
                so = a_branch[:leftp] if leftp>-1 else a_branch
                src = os.path.join(source_root, a_branch)
                dst = os.path.join(target_root, so, a_branch, device)
                print(dst)
                if not os.path.exists(dst):
                    os.makedirs(dst)
                # todo actual copy from a folder to another
                idt_copytree(src, dst)


if __name__ == "__main__":
    kbro_pm_xlsx_file_name = 'KBRO PM.xlsx'
    str_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    pm_execute_ops(kbro_pm_xlsx_file_name, str_time)


# kbro_pm_xlsx_file_name = "KBRO PM_20201102_FrankKu.xlsx"
# kbro_pm_xlsx_file_name = "KBRO PM_20201102_JOY.xlsx"
# kbro_pm_xlsx_file_name = "KBRO PM_20210125_CGNAT.xlsx"
# kbro_pm_xlsx_file_name = 'KBRO PM_20210201_SSH_N9K.xlsx'
# 傅星霖的多command
# kbro_pm_xlsx_file_name = "KBRO PM-Upstream SNR-All.xlsx"

