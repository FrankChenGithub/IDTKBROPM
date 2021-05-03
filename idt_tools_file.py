import os
from os import listdir
from os.path import isfile, join
import chardet
import datetime

# asr_asr_dict = {
#     "豐盟_FM": ["10.222.80.232", "10.222.80.234"],
#     "新頻道_NCC": ["10.222.88.232", "10.222.88.234"],
#     "全聯_UC": ["10.222.56.232", "10.222.56.234"],
#     "北桃園_BNT": ["10.222.64.232", "10.222.64.234"],
#     "大安_DA": ["10.222.40.232", "10.222.40.234"],
#     "大新店_CG": ["10.222.112.232", "10.222.112.234"],
#     "振道_HC": ["10.222.72.232", "10.222.72.234"],
#     "文山_WS": ["10.222.44.232", "10.222.44.234"],
#     "新台北_NTP": ["10.222.24.232", "10.222.24.234"],
#     "新唐城_TC": ["10.222.48.232", "10.222.48.234"],
#     "金頻道_KP": ["10.222.32.232", "10.222.32.234"],
#     "陽明山_YMS": ["10.222.16.232", "10.222.16.234"],
#     "永佳樂_YJL": ["192.168.136.232", "192.168.136.234"],
#     "紅樹林_MCT": ["192.168.144.232", "192.168.144.234"],
#     "聯禾_UCT": ["192.168.160.232", "192.168.160.234"],
#     "觀天下_GVC": ["192.168.152.232", "192.168.152.234"],
#     "南天_NT": ["10.222.96.232", "10.222.96.234"],
#     "觀昇_KS": ["10.222.104.232", "10.222.104.234"],
#     "鳳信_PHC": ["192.168.169.232", "192.168.169.234"],
#     "瑞湖_RHT": ["10.220.0.242", "10.220.0.244"],
#     "瑞湖_RHK": ["10.220.0.232", "10.220.0.234"],
#     "世大運_YJLT": ["192.168.136.236", "192.168.136.238"],
#     "LAB": ["10.222.2.229", "10.222.2.234"]
# }
# case_dict = {
#                 "豐盟_FM01": ["10.222.80.232", "10.222.80.204"],
#                 "豐盟_FM02": ["10.222.80.234", "10.222.80.205"],
#                 "新頻道_NCC01": ["10.222.88.232", "10.222.88.204"],
#                 "新頻道_NCC02": ["10.222.88.234", "10.222.88.205"],
#                 "全聯_UC01": ["10.222.56.232", "10.222.56.204"],
#                 "全聯_UC02": ["10.222.56.234", "10.222.56.205"],
#                 "北桃園_BNT01": ["10.222.64.232", "10.222.64.204"],
#                 "北桃園_BNT02": ["10.222.64.232", "10.222.64.205"],
#                 "大安_DA01": ["10.222.40.232", "10.222.40.204"],
#                 "大安_DA02": ["10.222.40.234", "10.222.40.205"],
#                 "大新店_CG01": ["10.222.112.232", "10.222.112.204"],
#                 "大新店_CG02": ["10.222.112.234", "10.222.112.205"],
#                 "振道_HC01": ["10.222.72.232", "10.222.72.204"],
#                 "振道_HC02": ["10.222.72.234", "10.222.72.205"],
#                 "文山_WS01": ["10.222.44.232", "10.222.44.204"],
#                 "文山_WS02": ["10.222.44.234", "10.222.44.205"],
#                 "新台北_NTP01": ["10.222.24.232", "10.222.24.204"],
#                 "新台北_NTP02": ["10.222.24.234", "10.222.24.205"],
#                 "新唐城_TC01": ["10.222.48.232", "10.222.48.204"],
#                 "新唐城_TC02": ["10.222.48.234", "10.222.48.205"],
#                 "金頻道_KP01": ["10.222.32.232", "10.222.32.204"],
#                 "金頻道_KP02": ["10.222.32.234", "10.222.32.205"],
#                 "陽明山_YMS01": ["10.222.16.232", "10.222.16.204"],
#                 "陽明山_YMS02": ["10.222.16.234", "10.222.16.205"],
#                 "永佳樂_YJL01": ["192.168.136.232", "192.168.136.204"],
#                 "永佳樂_YJL02": ["192.168.136.234", "192.168.136.205"],
#                 "紅樹林_MCT01": ["192.168.144.232", "192.168.144.204"],
#                 "紅樹林_MCT02": ["192.168.144.234", "192.168.144.205"],
#                 "聯禾_UCT01": ["192.168.160.232", "192.168.160.204"],
#                 "聯禾_UCT02": ["192.168.160.234", "192.168.160.205"],
#                 "觀天下_GVC01": ["192.168.152.232", "192.168.152.204"],
#                 "觀天下_GVC02": ["192.168.152.234", "192.168.152.205"],
#                 "南天_NT01": ["10.222.96.232", "10.220.96.204"],
#                 "南天_NT02": ["10.222.96.234", "10.220.96.205"],
#                 "觀昇_KS01": ["10.222.104.232", "10.222.104.204"],
#                 "觀昇_KS02": ["10.222.104.234", "10.222.104.205"],
#                 "鳳信_PHC01": ["192.168.169.232", "192.168.169.204"],
#                 "鳳信_PHC02": ["192.168.169.234", "192.168.169.205"],
#                 "LAB01": ["10.222.2.232", "10.222.2.123"],
#                 "LAB02": ["10.222.2.234", "10.222.2.123"],
#                 "LAB03": ["10.222.2.229", "10.222.2.123"]
# }
import openpyxl


def folder_to_device_name(device_dir):
    base_name = os.path.basename(os.path.normpath(device_dir))
    if base_name.find("AR01") > 0:
        return "AR01"
    elif base_name.find("AR02") > 0:
        return "AR02"
    elif base_name.find("ASR01") > 0:
        return "ASR01"
    elif base_name.find("ASR02") > 0:
        return "ASR02"


def xlsx_file_writable(xlsx):
    try:
        wb = openpyxl.load_workbook(filename=xlsx)
        wb.save(xlsx)
        wb.close()
        return True
    except:
        return False


def xlsx_col_num_to_string(n):
    string = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        string = chr(65 + remainder) + string
    return string


def get_file_encoding(logfile):
    rawdata = open(logfile, "rb").read()
    result = chardet.detect(rawdata)
    charenc = result['encoding']
    encoding = "utf-8"
    if charenc == "UTF-16":
        encoding = "utf-16"
    return encoding


def find_ip_from_file_name(file_name_with_ip_in_parenthese):
    left_idx = file_name_with_ip_in_parenthese.find("(")
    right_idx = file_name_with_ip_in_parenthese.find(")")
    ip = file_name_with_ip_in_parenthese[left_idx+1:right_idx]
    return ip


def is_first_time_or_ips(working_directory):
    # check the existence of the
    ar_before = ""
    ar_after = ""
    asr_before = ""
    asr_after = ""
    asr_ip = ""
    ar_ip = ""

    log_files = [f for f in listdir(working_directory)
                 if f[-3:] == "txt" and isfile(join(working_directory, f))]

    if len(log_files) == 0:
        return [True, asr_before, asr_ip, ar_before, ar_ip, asr_after, ar_after]

    for log_file in log_files:
        file_upper = log_file.upper()
        if file_upper.find("ASR") > -1:
            if file_upper.find("BEFORE") > -1:
                asr_before = log_file
            elif file_upper.find("AFTER") > -1:
                asr_after = log_file
        elif file_upper.find("AR") > -1:
            if file_upper.find("BEFORE") > -1:
                ar_before = log_file
            elif file_upper.find("AFTER") > -1:
                ar_after = log_file
    if asr_before == "" or ar_before == "":
        return [True, asr_before, asr_ip, ar_before, ar_ip, asr_after, ar_after]
    else:
        # FM_AR01(10.222.2.123)_20200831_AFTER
        asr_ip = find_ip_from_file_name(asr_before)
        ar_ip = find_ip_from_file_name(ar_before)
        return [False, asr_before, asr_ip, ar_before, ar_ip, asr_after, ar_after]


def is_first_time_or_ips_hc_version(working_directory, earliest=True):
    # check the existence of the
    ar_before = ""
    ar_after = ""
    asr_before = ""
    asr_after = ""
    asr_ip = ""
    ar_ip = ""

    log_files = [f for f in listdir(working_directory)
                 if f[-3:] == "txt" and isfile(join(working_directory, f))]

    if len(log_files) == 0:
        return [True, asr_before, asr_ip, ar_before, ar_ip]

    if earliest:
        log_files = sorted(log_files)
    else:
        log_files = sorted(log_files, reverse=True)

    asr_files = [log_file for log_file in log_files if log_file.find("ASR") > -1]
    ar_files = [log_file for log_file in log_files if log_file.find("AR") > -1]
    if len(asr_files) == 0 or len(ar_files) == 0:
        # 如果只有一個檔案在裡面，是否把它清掉
        return [True, asr_before, asr_ip, ar_before, ar_ip]
    else:
        # 北桃園_BNT01_healthcheck-AR(10.222.64.204)-20200921164835
        [asr_before, ar_before] = [asr_files[0], ar_files[0]]
        asr_ip = find_ip_from_file_name(asr_before)
        ar_ip = find_ip_from_file_name(ar_before)
        return [False, asr_before, asr_ip, ar_before, ar_ip]


# TODO FrankChen 20200926 new directory structure for health check
#  Root/health_check/site/case/...
#  Root/health_check/北桃園BTN/北桃園BTN01/AR01(ar01_ip)....txt
#  Root/health_check/北桃園BTN/北桃園BTN01/ASRV01(asr01_ip)....txt
#  Root/health_check/北桃園BTN/北桃園BTN02/AR02(ar02_ip)....txt
#  Root/health_check/北桃園BTN/北桃園BTN02/ASRV02(asr02_ip)....txt
#  working_diectory == Root/health_check
def hc_is_first_time_or_ips_time_bound_version(hc_dir, earliest=True, not_time_bound=True):
    result_list = []
    for dirPath, dirNames, fileNames in os.walk(hc_dir):
        if len(fileNames) > 0:
            case_name = os.path.basename(dirPath)
            print(dirPath, fileNames)
            if len(case_name) < 20:
                log_txt_files = [f for f in fileNames if f[-3:] == "txt"]
                if len(log_txt_files) > 1:
                    for i, f in enumerate(log_txt_files, start=0):
                        print(i, f)
                    postfix = case_name[-2:]
                    print("case:", case_name, postfix)
                    if earliest:
                        log_files = sorted(log_txt_files)
                    else:
                        log_files = sorted(log_txt_files, reverse=True)
                    asr_files = [log_file for log_file in log_files if log_file.find("ASR") > -1]
                    ar_files = [log_file for log_file in log_files if log_file.find("AR") > -1]
                    if not_time_bound:
                        [asr_before, ar_before] = [asr_files[0], ar_files[0]]
                        asr_ip = find_ip_from_file_name(asr_before)
                        ar_ip = find_ip_from_file_name(ar_before)
                        result_list.append(["ASRV" + postfix, asr_ip, case_name, os.path.join(dirPath, asr_before)])
                        result_list.append(["AR" + postfix, ar_ip, case_name, os.path.join(dirPath, ar_before)])
                    else:
                        # todo 20201224 FrankChen 5~8點如果有log檔，取最後一個當before，不然就是取8點以後的第一個log檔案
                        asr_before = get_time_bound_first_file(asr_files)
                        if asr_before != "":
                            asr_ip = find_ip_from_file_name(asr_before)
                            result_list.append(["ASRV" + postfix, asr_ip, case_name, os.path.join(dirPath, asr_before)])
                        ar_before = get_time_bound_first_file(ar_files)
                        if ar_before != "":
                            ar_ip = find_ip_from_file_name(ar_before)
                            result_list.append(["AR" + postfix, ar_ip, case_name, os.path.join(dirPath, ar_before)])
    return result_list


def get_time_bound_first_file(device_file_list):
    today = datetime.datetime.now().strftime("%Y%m%d")
    str_t1 = "030000"
    str_t2 = "080000"
    # str_t1 = "150000"
    # str_t2 = "163000"
    time_bound_start = int(today + str_t1)
    time_bound_end = int(today + str_t2)
    on_site_file = ""
    babysitting_file = ""
    for txt in device_file_list:
        txt_time = int(txt.split("-")[-1][:-4])
        if time_bound_start <= txt_time <= time_bound_end:
            on_site_file = txt
            print(txt_time, txt)
        elif time_bound_end <= txt_time:
            # todo 如果出現只取第一個
            if babysitting_file == "":
                babysitting_file = txt
    if on_site_file != "":
        return on_site_file
    else:
        return babysitting_file

def ops_get_file_name_list(ops_so_dir, earliest=True, keyword="A"):
    result_list = []
    keyword = keyword.upper()
    for dirPath, dirNames, fileNames in os.walk(ops_so_dir):
        if len(fileNames) > 0:
            case_name = os.path.basename(dirPath)
            print(dirPath, fileNames)
            if len(case_name) < 20:
                log_txt_files = [f for f in fileNames if f[-3:] == "txt"]
                if len(log_txt_files) > 0:
                    for i, f in enumerate(log_txt_files, start=0):
                        print(i, f)
                    postfix = case_name[-2:]
                    print("case:", case_name, postfix)
                    if earliest:
                        log_files = sorted(log_txt_files)
                    else:
                        log_files = sorted(log_txt_files, reverse=True)
                    asr_files = [log_file for log_file in log_files if log_file.upper().find(keyword) > -1
                                 and log_file.upper().find("ASR") > -1]
                    ar_files = [log_file for log_file in log_files if log_file.upper().find(keyword) > -1
                                and log_file.upper().find("AR") > -1]
                    if len(asr_files) > 0:
                        asr_ip = find_ip_from_file_name(asr_files[0])
                        result_list.append(["ASR" + postfix, asr_ip, case_name, os.path.join(dirPath, asr_files[0])])
                    if len(ar_files) > 0:
                        ar_ip = find_ip_from_file_name(ar_files[0])
                        result_list.append(["AR" + postfix, ar_ip, case_name, os.path.join(dirPath, ar_files[0])])
    return result_list


def is_first_time_or_ips_b4af_version(b4af_dir, earliest=True):
    result_list = []
    for dirPath, dirNames, fileNames in os.walk(b4af_dir):
        if len(fileNames) > 0:
            case_name = os.path.basename(dirPath)
            print(dirPath, fileNames)
            if len(case_name) < 20:
                log_txt_files = [f for f in fileNames if f[-3:] == "txt"]
                if len(log_txt_files) > 0:
                    for i, f in enumerate(log_txt_files, start=0):
                        print(i, f)
                    postfix = case_name[-2:]
                    print("case:", case_name, postfix)
                    if earliest:
                        log_files = sorted(log_txt_files)
                    else:
                        log_files = sorted(log_txt_files, reverse=True)
                    asr_files = [log_file for log_file in log_files if log_file.find("ASR") > -1]
                    ar_files = [log_file for log_file in log_files if log_file.find("AR") > -1]
                    if len(asr_files) > 0:
                        asr_ip = find_ip_from_file_name(asr_files[0])
                        result_list.append(["ASR" + postfix, asr_ip, case_name, os.path.join(dirPath, asr_files[0])])
                    if len(ar_files) > 0:
                        ar_ip = find_ip_from_file_name(ar_files[0])
                        result_list.append(["AR" + postfix, ar_ip, case_name, os.path.join(dirPath, ar_files[0])])
    return result_list



def is_first_time_asr_before_after(working_directory):
    # check the existence of the
    asrv01_before = ""
    asrv01_after = ""
    asrv02_before = ""
    asrv02_after = ""
    asrv01_ip = ""
    asrv02_ip = ""

    log_files = [f for f in listdir(working_directory)
                 if f[-3:] == "txt" and isfile(join(working_directory, f))]

    if len(log_files) == 0:
        return [True, asrv01_before, asrv01_ip, asrv02_before, asrv02_ip, asrv01_after, asrv02_after]

    for log_file in log_files:
        file_upper = log_file.upper()
        if file_upper.find("ASRV01") > -1:
            if file_upper.find("BEFORE") > -1:
                asrv01_before = log_file
            elif file_upper.find("AFTER") > -1:
                asrv01_after = log_file
        elif file_upper.find("ASRV02") > -1:
            if file_upper.find("BEFORE") > -1:
                asrv02_before = log_file
            elif file_upper.find("AFTER") > -1:
                asrv02_after = log_file
    if asrv01_before == "" or asrv02_before == "":
        return [True, asrv01_before, asrv01_ip, asrv02_before, asrv02_ip, asrv01_after, asrv02_after]
    else:
        # FM_AR01(10.222.2.123)_20200831_AFTER
        asrv01_ip = find_ip_from_file_name(asrv01_before)
        asrv02_ip = find_ip_from_file_name(asrv02_before)
        return [False, asrv01_before, asrv01_ip, asrv02_before, asrv02_ip, asrv01_after, asrv02_after]


def get_asr_before_files(working_directory):
    # check the existence of the
    asrv01_before = ""
    asrv02_before = ""

    log_files = [f for f in listdir(working_directory)
                 if f[-3:] == "txt" and isfile(join(working_directory, f))]

    if len(log_files) > 0:
        for log_file in log_files:
            file_upper = log_file.upper()
            if file_upper.find("ASRV01") > -1:
                if file_upper.find("BEFORE") > -1:
                    asrv01_before = log_file
            elif file_upper.find("ASRV02") > -1:
                if file_upper.find("BEFORE") > -1:
                    asrv02_before = log_file
    return [asrv01_before, asrv02_before]


def separate_show_command_to_files_sequentially(log_folder, log_file_name):
    # TODO 先將不同的show command 分開為不同的檔案
    print(log_folder, log_file_name)
    file_name_without_extension = log_file_name[:-4]
    data_dir = os.path.join(log_folder, file_name_without_extension)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    hash_show = "show"
    hash = "#"
    full_file_name = os.path.join(log_folder, log_file_name)
    log_file = open(full_file_name, "r", encoding=get_file_encoding(full_file_name))
    lines = log_file.readlines()
    data_file_name = ""
    individual_show_file = None
    file_count = 0
    for line in lines:
        show_index = line.find(hash_show)
        hash_index = line.find(hash)
        if -1 < hash_index < show_index:
            # TODO open a new file
            command = ' '.join(line[show_index:].strip().split()).lower()
            if data_file_name != "":
                individual_show_file.close()
            file_count += 1
            data_file_name = "show_{:02d}".format(file_count)
            full_file_name = os.path.join(data_dir, data_file_name)
            individual_show_file = open(full_file_name, "w", encoding="utf-8")
            individual_show_file.write(line)
        else:
            if data_file_name != "":
                individual_show_file.write(line)

    if data_file_name != "":
        individual_show_file.close()


def txt_remove_blank_line_in_file(txt_file_full_path):
    # formatted_eventtime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    # temp_txt_file = os.path.join(os.path.dirname(txt_file_full_path), formatted_eventtime + "_temp.txt")
    temp_txt_file = txt_file_full_path + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + "_temp.txt"
    print("temp_txt_file:", temp_txt_file)
    f = open(txt_file_full_path, "r", encoding="utf-8")
    lines = f.readlines()
    f.close()

    f2 = open(temp_txt_file, "w", encoding="utf-8")
    for line in lines:
        if len(line.strip()) > 0:
            f2.write(line.rstrip() + "\n")
    f2.close()
    os.remove(txt_file_full_path)
    os.rename(temp_txt_file, txt_file_full_path)


def txt_remove_lines_before_show_commands_in_file(txt_file_full_path):
    formatted_eventtime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    # temp_txt_file = os.path.join(os.path.dirname(txt_file_full_path), formatted_eventtime + "_temp.txt")
    temp_txt_file = txt_file_full_path + datetime.datetime.now().strftime("%H%M%S") + "_temp.txt"
    print(temp_txt_file)
    f = open(txt_file_full_path, "r", encoding="utf-8")
    lines = f.readlines()
    f.close()

    f2 = open(temp_txt_file, "w", encoding="utf-8")
    af_show_cmd = False
    for line in lines:
        if -1 < line.find("#") < line.find("show"):
            af_show_cmd = True
            f2.write(line.rstrip() + "\n")
        elif af_show_cmd:
            if len(line.strip()) > 0:
                f2.write(line.rstrip() + "\n")
    f2.close()
    os.remove(txt_file_full_path)
    os.rename(temp_txt_file, txt_file_full_path)
