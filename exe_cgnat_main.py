import datetime
import sys
import os
import multiprocessing as mp
import idt_tools_citrix_netscaler as idtssh
import exe_cgnat_counting_mp_version as idtcgnat

debug_mode = False
ide_mode = False
work_dir = os.getcwd()
so_ip_infos = [["10.220.96.24",   "NT_CGNAT1",  "南天",  "citrix_pm", "citrix_pm@123"],
               ["192.168.169.24", "PHC_CGNAT1", "鳳信",  "citrix_pm", "citrix_pm@123"],
               ["10.222.56.24",   "UC_CGNAT1", "全聯",  "citrix_pm", "citrix_pm@123"],
               ["10.222.88.25",   "NCC_CGNAT2", "新頻道", "citrix_pm", "citrix_pm@123"],
               ["10.222.64.24",   "BNT_CGNAT1", "北桃園", "citrix_pm", "citrix_pm@123"],
               ["10.222.104.25",  "KS_CGNAT2",  "觀昇",  "citrix_pm", "citrix_pm@123"],
               ["192.168.160.40", "UCT_CGNAT1", "聯禾",  "citrix_pm", "citrix_pm@123"],
               ["10.222.32.24",   "KP_CGNAT1",  "金頻道", "citrix_pm", "citrix_pm@123"],
               ["192.168.136.24", "YJL_CGNAT1", "永佳樂", "citrix_pm", "citrix_pm@123"],
               ["10.222.80.24",   "FM_CGNAT1",  "豐盟",  "citrix_pm", "citrix_pm@123"]
               ]


def process_command_line_args(args):
    global debug_mode
    global work_dir
    global ide_mode
    print('Number of arguments:', len(args), 'arguments.')
    print('Argument List:', str(args))
    for arg_idx, arg in enumerate(args, start=0):
        print(arg_idx, arg)
        if arg == "-debug":
            debug_mode = True
        elif arg == "-wdir":
            work_dir = args[arg_idx+1]

    print("work_dir", work_dir)
    if args[0].lower().endswith(".py"):
        ide_mode = True


if __name__ == "__main__":
    # todo 分3個區段執行
    #  1. ssh取得log檔案 (multiprocessing)
    #  2. ParseLog(pl or exe)分解log為csv檔案(multiprocessing)
    #  3. csv檔案統計至xlsx
    mp.freeze_support()
    process_command_line_args(sys.argv)
    print("ide_mode" if ide_mode else "exe_mode")
    time_start = datetime.datetime.now()
    xminute = datetime.datetime.now().strftime("%Y%m%d%H%M")
    data_dir = os.path.join(work_dir, xminute)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    # 1. ssh取得log檔案 (multiprocessing)
    ssh_procs = []
    for so_ip_info in so_ip_infos:
        xtime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        device_ip, device_host, device_so, device_user, device_pw = so_ip_info
        proc = mp.Process(target=idtssh.cgnat_show_lsn_session_worker,
                          args=(device_ip, device_host, device_so, data_dir, device_user, device_pw, xtime))
        ssh_procs.append(proc)
        proc.start()

    for proc in ssh_procs:
        proc.join()

    # 2. ParseLog(pl or exe)分解log為csv檔案(multiprocessing)
    idtcgnat.cgnat_mp_logparsing_ide(work_dir, xminute, ide_mode)
    #  3. csv檔案統計至xlsx
    idtcgnat.cgnat_csvs_to_xlsx(work_dir, xminute)
    time_end = datetime.datetime.now()
    print("ide_mode" if ide_mode else "exe_mode")
    print("start@", time_start)
    print("end@", time_end)
    print("total:", time_end - time_start)
