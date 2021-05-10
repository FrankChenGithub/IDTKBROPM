
import re, os, time, datetime, telnetlib, linecache
import shutil
import sys
import traceback

from selenium import webdriver
import urllib.request as urllib2
import idt_tools_pdf
from urllib.parse import quote_plus as url_quoteplus
from urllib.parse import urlsplit
from selenium.webdriver.common.by import By as WebBy
from selenium.webdriver.support.ui import Select as WebSelect
import idt_tools_constant_pm as idtconst
import idt_tools_word as idtword

str_log = idtconst.str_log

##設定PDF 頁面的參數
def convert_pdf(FOLDER, FILENAMEPDF):
    # FOLDER: LOG/豐盟/ASR/
    # filename: PDF is FOX1729GWHJ_FM-I-ASR-02.pdf
    print("filename PDF is %s" % FILENAMEPDF)
    NEWFILEPDF = os.path.join(FOLDER, FILENAMEPDF)
    if os.path.isfile(NEWFILEPDF):
        os.remove(NEWFILEPDF)
    temp_pdf_folder = os.path.join(os.getcwd(), "pdf_temp_" + FILENAMEPDF[:-4])
    idt_tools_pdf.txt_file_to_command_first_page_pdf(os.getcwd(), "temp.txt", temp_pdf_folder, FILENAMEPDF)

    if os.path.isfile(FILENAMEPDF):
        os.rename(FILENAMEPDF, NEWFILEPDF)
    if os.path.isfile('temp.txt'):
        os.remove('temp.txt')
    if os.path.exists(temp_pdf_folder):
        shutil.rmtree(temp_pdf_folder)


##列印選取內容
def OLD_get_content(FILENAME, HOST, device_cmds):
    ##確認檔案是否存在
    if os.path.exists(FILENAME):
        data_list = []
        content = ' '
        #  TODO　20200915-07
        fp = open("temp.txt", "w")
        file_data = ' '
        file_data = linecache.getlines(FILENAME)

        # bk = xlrd.open_workbook('KBRO PM.xlsx')
        # bk = xlrd.open_workbook(idtconst.pm_xlsx_file_name)
        #
        # shxrange = range(bk.nsheets)
        # sh = bk.sheet_by_name("ASR")
        # nrows = sh.nrows

        ##讀取Execl 內指令,比對XXXXXX.txt內相同的行數
        for file_data_line in range(len(file_data)):
            for row_command in device_cmds:
                # row_command = sh.cell_value(execl_line, 0)
                command = "RP/0/RSP0/CPU0:" + HOST + "#" + row_command + "\n"
                # 比對資料是否相符
                if file_data[file_data_line] == command:
                    data_list.extend([file_data_line])

        for data_list_line in range(len(data_list)):
            ##讀取XXXXXX.txt 列印資料
            data_len = 109
            one_page_line = 80
            page_capture_line = 70
            half_page = 20
            less_page1 = 0
            more_page1 = 0
            more_page2 = 0

            line_no = int(data_list[data_list_line])
            next = data_list_line + 1

            ##讀取下一筆行數
            if next < len(data_list):
                line_next = int(data_list[next])
            ##最後一筆行數
            elif next == len(data_list):
                line_next = len(file_data)

            ##比對前後兩筆行數差多少行
            sub_line = int(line_next - line_no)
            # print "########################"
            # print "file_data is %s" % len(file_data)
            # print "line_no is %s" % line_no
            # print "line_next is %s" % line_next
            # print "sub_line is %s" % sub_line
            # print "content is %s" % file_data[line_no]
            # print "########################"

            ########################################
            ##比對前後兩筆相差的行數比一頁 80行還多
            ########################################
            if (sub_line > one_page_line):
                # 統計資料超過一行
                for more_line in range(page_capture_line):
                    more_data_len = len(file_data[line_no + more_line])
                    if more_data_len > data_len:
                        more_page1 = more_page1 + 1

                    # print "file_data_len is %s"% more_data_len
                    # print "file_data is %s"% file_data[line_no + more_line]

                # print "more_page1 is %s" %more_page1
                for more_half_line in range(more_page1):
                    more_data_len_1 = len(file_data[line_no + more_half_line])
                    if more_data_len_1 > data_len:
                        more_page2 = more_page2 + 1

                # print "more_page2 is %s" %more_page2
                ##超過一行的行數超過半頁
                if more_page1 > half_page:

                    # 列印符合內容
                    for more_print_line in range(more_page1):
                        content = file_data[line_no + more_print_line]
                        fp.write(content)

                    # 列印空白行數
                    for more_print_line in range(one_page_line - more_page1 - more_page2):
                        content = "\n"
                        fp.write(content)
                # print "more_page1 > half_page is %s" % more_print_line
                # 超過一行的行數少於半頁
                if more_page1 < half_page:

                    # 列印符合內容
                    for more_print_half_line in range(page_capture_line):
                        content = file_data[line_no + more_print_half_line]
                        fp.write(content)

                    # 列印空白行數
                    for more_print_half_space_line in range(one_page_line - page_capture_line - more_page1):
                        content = "\n"
                        fp.write(content)
                # print "more_page1 < half_page"
            # print "sub_line > one_page_line"
            ########################################
            ##比對前後兩筆相差的行數比一頁 80行還少
            ########################################
            elif (sub_line < one_page_line):
                # 列印資料
                for less_line in range(sub_line):
                    less_data_len = len(file_data[line_no + less_line])
                    if less_data_len > data_len:
                        less_page1 = less_page1 + 1

                    # 列印符合內容
                    content = file_data[line_no + less_line]
                    fp.write(content)
                # print "less_page1 is %s"%less_page1
                # 列印空白行
                for less_print_space_line in range(80 - sub_line - less_page1):
                    content = "\n"
                    fp.write(content)
            # print "sub_line < one_page_line"
        fp.close

    else:
        # TODO FrankChen 20200915-04 change path to FILENAME
        print('the path [{}] is not exist!'.format(FILENAME))


def get_content(FILENAME, HOST, device_cmds):
    ##確認檔案是否存在
    if os.path.exists(FILENAME):
        data_list = []
        content = ' '
        #  TODO　20200915-07
        fp = open("temp.txt", "w")
        file_data = ' '
        file_data = linecache.getlines(FILENAME)

        ##讀取Execl 內指令,比對XXXXXX.txt內相同的行數
        for file_data_line in range(len(file_data)):
            for row_command in device_cmds:
                # row_command = sh.cell_value(execl_line, 0)
                command = "RP/0/RSP0/CPU0:" + HOST + "#" + row_command + "\n"
                # 比對資料是否相符
                if file_data[file_data_line] == command:
                    data_list.extend([file_data_line])

        for data_list_line in range(len(data_list)):
            ##讀取XXXXXX.txt 列印資料
            data_len = 109
            one_page_line = 80
            page_capture_line = 70
            half_page = 20
            less_page1 = 0
            more_page1 = 0
            more_page2 = 0

            line_no = int(data_list[data_list_line])
            next = data_list_line + 1

            ##讀取下一筆行數
            if next < len(data_list):
                line_next = int(data_list[next])
            ##最後一筆行數
            elif next == len(data_list):
                line_next = len(file_data)

            ##比對前後兩筆行數差多少行
            sub_line = int(line_next - line_no)
            # print "########################"
            # print "file_data is %s" % len(file_data)
            # print "line_no is %s" % line_no
            # print "line_next is %s" % line_next
            # print "sub_line is %s" % sub_line
            # print "content is %s" % file_data[line_no]
            # print "########################"

            ########################################
            ##比對前後兩筆相差的行數比一頁 80行還多
            ########################################
            if (sub_line > one_page_line):
                # 統計資料超過一行
                for more_line in range(page_capture_line):
                    more_data_len = len(file_data[line_no + more_line])
                    if more_data_len > data_len:
                        more_page1 = more_page1 + 1

                    # print "file_data_len is %s"% more_data_len
                    # print "file_data is %s"% file_data[line_no + more_line]

                # print "more_page1 is %s" %more_page1
                for more_half_line in range(more_page1):
                    more_data_len_1 = len(file_data[line_no + more_half_line])
                    if more_data_len_1 > data_len:
                        more_page2 = more_page2 + 1

                # print "more_page2 is %s" %more_page2
                ##超過一行的行數超過半頁
                if more_page1 > half_page:

                    # 列印符合內容
                    for more_print_line in range(more_page1):
                        content = file_data[line_no + more_print_line]
                        fp.write(content)

                    # 列印空白行數
                    for more_print_line in range(one_page_line - more_page1 - more_page2):
                        content = "\n"
                        fp.write(content)
                # print "more_page1 > half_page is %s" % more_print_line
                # 超過一行的行數少於半頁
                if more_page1 < half_page:

                    # 列印符合內容
                    for more_print_half_line in range(page_capture_line):
                        content = file_data[line_no + more_print_half_line]
                        fp.write(content)

                    # 列印空白行數
                    for more_print_half_space_line in range(one_page_line - page_capture_line - more_page1):
                        content = "\n"
                        fp.write(content)
                # print "more_page1 < half_page"
            # print "sub_line > one_page_line"
            ########################################
            ##比對前後兩筆相差的行數比一頁 80行還少
            ########################################
            elif (sub_line < one_page_line):
                # 列印資料
                for less_line in range(sub_line):
                    less_data_len = len(file_data[line_no + less_line])
                    if less_data_len > data_len:
                        less_page1 = less_page1 + 1

                    # 列印符合內容
                    content = file_data[line_no + less_line]
                    fp.write(content)
                # print "less_page1 is %s"%less_page1
                # 列印空白行
                for less_print_space_line in range(80 - sub_line - less_page1):
                    content = "\n"
                    fp.write(content)
            # print "sub_line < one_page_line"
        fp.close

    else:
        # TODO FrankChen 20200915-04 change path to FILENAME
        print('the path [{}] is not exist!'.format(FILENAME))


def telNetCall(IP, HOST, SO, DEVICE, ID, PW, device_cmds):
    global telnet
    output = " "
    data = " "
    # 如果沒有值傳進來，則使用預設帳密
    if ID == "" and PW == "":
        print("FRANK no row_id, row_pw used default")
        ID = idtconst.pm_user
        PW = idtconst.pm_pw

    # FOLDER = "LOG/%s/%s/" % (DEVICE, SO)
    FOLDER = "{}/{}/{}/".format(str_log, DEVICE, SO)
    if not os.path.exists(FOLDER):
        os.makedirs(FOLDER)

    ############################################################
    # get HOST & SN
    ############################################################
    print("{} {} ({}) 01  @ {}".format(HOST, DEVICE, IP, datetime.datetime.now()))
    ###########telnet ASR##########
    if (DEVICE == "ASR"):
        telnet = telnetlib.Telnet(IP, port=23, timeout=10)
        telnet.read_until('username: '.encode(), 3)
        telnet.write(ID.encode('ascii') + b'\r\n')
        telnet.read_until('password: '.encode(), 3)
        telnet.write(PW.encode('ascii') + b'\r\n')
        telnet.write(b"terminal length 0 \r\n")
        telnet.write(b"admin show dsc \r\n")
        telnet.write(b"show run hostname \r\n")
        time.sleep(1)
        telnet.write(b"exit \r\n")
        data = " "
        data = telnet.read_all().decode('ascii').split()
        SNindex = data.index("PRIMARY-DSC")
        SN = data[SNindex - 1]

        HOSTindex = data.index("hostname")
        HOST = data[HOSTindex + 7]

    ###########telnet CMTS ##########
    elif (DEVICE == "uBR10K") or (DEVICE == "cBR8") or (DEVICE == "Switch"):

        telnet = telnetlib.Telnet(IP, port=23, timeout=10)
        telnet.read_until('username: '.encode(), 3)
        telnet.write(ID.encode('ascii') + b'\r\n')
        telnet.read_until('password: '.encode(), 3)
        telnet.write(PW.encode('ascii') + b'\r\n')
        telnet.write(b"terminal length 0 \r\n")
        telnet.write(b"show run | i hostname \r\n")
        telnet.write(b"show inventory \r\n")
        telnet.write(b"exit \r\n")

        data = " "
        data = telnet.read_all().decode('ascii').split()
        # print "data is %s"% data
        SNindex = data.index("SN:")
        SN = data[SNindex + 1]
        HOSTindex = data.index("hostname")
        HOST = data[HOSTindex + 2]

    ###########telnet DTI ##########
    elif (DEVICE == "DTI"):
        ID = "admin"
        PW = "SymmTC1000"
        telnet = telnetlib.Telnet(IP, port=23, timeout=10)
        telnet.read_until('login: '.encode(), 3)
        telnet.write(ID.encode('ascii') + b'\r\n')
        telnet.read_until('Password: '.encode(), 3)
        telnet.write(PW.encode('ascii') + b'\r\n')
        telnet.write(b"show hostname \r\n")
        telnet.write(b"show inventory \r\n")
        time.sleep(1)
        telnet.write(b"logout \r\n")

        output = " "
        output = telnet.read_all().decode('ascii')
        ansi_escape = re.compile(r'\x1b[^m]*m')
        output = ansi_escape.sub('', output)

        data = " "
        data = output.split()

        SNindex = data.index("Tag")
        SN = data[SNindex + 2]
        HOSTindex = data.index("name")
        HOST = data[HOSTindex + 2]

    print("{} {} ({}) 02  @ {}".format(HOST, DEVICE, IP, datetime.datetime.now()))
    if (DEVICE == "uBR10K") or (DEVICE == "cBR8") or (DEVICE == "ASR") or (DEVICE == "DTI") or (DEVICE == "Switch"):
        # FILENAME = FOLDER + "%s_%s.txt" % (SN, HOST)
        # FILENAMEPDF = "%s_%s.pdf" % (SN, HOST)
        FILENAME = os.path.join(FOLDER, "{} {}_{}.txt".format(SO, SN, HOST))
        FILENAMEPDF = "{} {}_{}.pdf".format(SO, SN, HOST)
        print("SN is %s" % SN)
        print("HOST is %s" % HOST)
        print("filename is %s\n" % (FILENAME))

    ############################################################
    # login CMTS or ASR
    ############################################################
    print("{} {} ({}) 03  @ {}".format(HOST, DEVICE, IP, datetime.datetime.now()))
    if (DEVICE == "uBR10K") or (DEVICE == "cBR8") or (DEVICE == "ASR") or (DEVICE == "Switch"):
        telnet = telnetlib.Telnet(IP, port=23, timeout=10)
        telnet.read_until('username: '.encode(), 3)
        telnet.write(ID.encode('ascii') + b'\r\n')
        telnet.read_until('password: '.encode(), 3)
        telnet.write(PW.encode('ascii') + b'\r\n')
        telnet.write(b"terminal length 0 \r\n")
        telnet.write(b"terminal width 0 \r\n")

        for row_command in device_cmds:
            print("command is %s" % (row_command))
            telnet.write(row_command.encode('ascii') + b'\r\n')

        telnet.write(b"exit \r\n")
        print("exit")
        print("{} {} ({}) 04 finish commands @ {}".format(HOST, DEVICE, IP, datetime.datetime.now()))
        output = " "
        # todo not to decode
        output = telnet.read_all().decode('ascii')
        print("{} {} ({}) 05 get and decode data @ {}".format(HOST, DEVICE, IP, datetime.datetime.now()))
        fp = open(FILENAME, "w")
        fp.write(output)
        fp.close
        print("{} {} ({}) 06 finish file @ {}".format(HOST, DEVICE, IP, datetime.datetime.now()))
        if DEVICE in ("ASR", "cBR8", "uBR10K"):
            # content = get_content(FILENAME, HOST, device_cmds)
            # convert_pdf(FOLDER, FILENAMEPDF)
            word_title = "{} {}_{}檢查報告".format(SO, SN, HOST)
            idtword.word_log_txt_file_to_docx(FILENAME, word_title)
            print("{} {} ({}) 07 word (.docx) file converted @ {}".format(HOST, DEVICE, IP, datetime.datetime.now()))

    ############################################################
    # login DTI
    ############################################################

    elif (DEVICE == "DTI"):
        ID = "admin"
        PW = "SymmTC1000"
        telnet = telnetlib.Telnet(IP, port=23, timeout=10)
        telnet.read_until('TimeCreator login: '.encode(), 3)
        telnet.write(ID.encode('ascii') + b'\r\n')
        telnet.read_until('Password: '.encode(), 3)
        telnet.write(PW.encode('ascii') + b'\r\n')

        for row_command in device_cmds:
            print("command is %s" % (row_command))
            telnet.write(row_command.encode('ascii') + b'\r\n')
        telnet.write(b"logout \r\n")
        print("logout")

        output = " "
        output = telnet.read_all().decode("ascii")
        ansi_escape = re.compile(r'\x1b[^m]*m')
        output = ansi_escape.sub('', output)
        # TODO 20200915-07 write to file 不要byte
        fp = open(FILENAME, "w")
        fp.write(output)
        fp.close

    ############################################################
    # login RFGW
    ############################################################

    elif (DEVICE == "RFGW"):
        # RFFOLDER = "LOG/%s/%s/%s" % (DEVICE, SO, HOST)
        RFFOLDER = "{}/{}/{}/{}".format(str_log, DEVICE, SO, HOST)
        if not os.path.exists(RFFOLDER):
            os.makedirs(RFFOLDER)

        chromedriver = "chromedriver/chromedriver.exe"
        browser = webdriver.Chrome(chromedriver)

        URL = "http://%s/login/login.cgi?mode=AUTH_LOGIN&params=admin|idtech&" % (IP)
        browser.get(URL)
        browser.maximize_window()

        ###########get host & SN##########
        HOSTURL = "http://%s/fs/about.html" % (IP)
        data = " "
        # TODO 20200915-08 urlopen 如果需要取值，也需要 decode('ascii') bytes to string
        data = urllib2.urlopen(HOSTURL).read().decode("ascii").split()
        HOSTindex = data.index("Cisco")
        HOST = data[HOSTindex - 11].rstrip('</td>')
        print("HOST is %s" % HOST)
        print(data)
        try:
            SNURL = "http://%s/common/getTableData.cgi?SYS_ABOUT" % (IP)
            print("SNURL", SNURL)
            # TODO 20200915-08
            SN = urllib2.urlopen(SNURL).read().decode("ascii")
            print("SN is %s" % (SN))
        except:
            print(sys.exc_info())
            print("Can't get SN from URL: %s" % (SNURL))
            var = traceback.format_exc()
            print(var)
            SN = HOST
        try:
            URL = "http://%s" % (IP)
            PICFOLDER = "%s/alarms.png" % (RFFOLDER)
            browser.get(URL)
            time.sleep(2)
            elem = browser.find_element_by_id("menu-alarms")
            elem.click()
            time.sleep(2)
            print("PICFOLDER1", PICFOLDER)
            browser.get_screenshot_as_file(PICFOLDER)
        except:
            print(sys.exc_info())
            print("Can't get pic from URL: %s" % (URL))
            var = traceback.format_exc()
            print(var)
        URL = "http://%s/fs/Summary_noappl.htm" % (IP)
        PICFOLDER = "%s/Summary_noappl.png" % (RFFOLDER)
        browser.get(URL)
        elem = browser.find_element_by_id("bandwidth")
        elem.click()
        browser.execute_script("document.body.style.zoom='60%'")
        time.sleep(4)
        print("PICFOLDER2", PICFOLDER)
        browser.get_screenshot_as_file(PICFOLDER)

        URL = "http://%s/fs/Inventory.html" % (IP)
        PICFOLDER = "%s/Inventory.png" % (RFFOLDER)
        browser.get(URL)
        time.sleep(2)
        print("PICFOLDER3", PICFOLDER)
        browser.get_screenshot_as_file(PICFOLDER)

        URL = "http://%s/fs/resource_utilization.htm" % (IP)
        PICFOLDER = "%s/resource_utilization.png" % (RFFOLDER)
        browser.get(URL)
        time.sleep(2)
        print("PICFOLDER4", PICFOLDER)
        browser.get_screenshot_as_file(PICFOLDER)

        URL = "http://%s/fs/about.html" % (IP)
        PICFOLDER = "%s/about.png" % (RFFOLDER)
        browser.get(URL)
        time.sleep(2)
        print("PICFOLDER5", PICFOLDER)
        browser.get_screenshot_as_file(PICFOLDER)

        URL = "http://%s/fs/temperature.html" % (IP)
        PICFOLDER = "%s/temperature.png" % (RFFOLDER)
        browser.get(URL)
        elem = browser.find_element_by_id("TempInF")
        elem.click()
        time.sleep(2)
        print("PICFOLDER6", PICFOLDER)
        browser.get_screenshot_as_file(PICFOLDER)

        URL = "http://%s/fs/Global_qam96_port_channel.htm" % (IP)
        PICFOLDER = "%s/Global_qam96_port_channel.png" % (RFFOLDER)
        browser.get(URL)
        browser.execute_script("document.body.style.zoom='70%'")
        time.sleep(2)
        print("PICFOLDER7", PICFOLDER)
        browser.get_screenshot_as_file(PICFOLDER)

        URL = "http://%s/fs/ip_config.htm" % (IP)
        PICFOLDER = "%s/ip_config.png" % (RFFOLDER)
        browser.get(URL)
        time.sleep(2)
        print("PICFOLDER8", PICFOLDER)
        browser.get_screenshot_as_file(PICFOLDER)

        URL = "http://%s/log/logmgr.cgi?mode=SAVE" % (IP)
        LOGFOLDER = "%s/%s_%s.txt" % (RFFOLDER, SN, HOST)
        output = urllib2.urlopen(URL)
        fp = open(LOGFOLDER, "wb")
        fp.write(output.read())

        browser.close()
        browser.quit()


def get_rfgw_http_screenshot(IP, HOST, SO, DEVICE):
    # RFFOLDER = "LOG/%s/%s/%s" % (DEVICE, SO, HOST)
    RFFOLDER = "{}/{}/{}/{}".format(str_log, DEVICE, SO, HOST)
    if not os.path.exists(RFFOLDER):
        os.makedirs(RFFOLDER)

    chromedriver = "chromedriver/chromedriver.exe"
    browser = webdriver.Chrome(chromedriver)

    URL = "http://%s/login/login.cgi?mode=AUTH_LOGIN&params=admin|idtech&" % (IP)
    browser.get(URL)
    browser.maximize_window()

    ###########get host & SN##########
    HOSTURL = "http://%s/fs/about.html" % (IP)
    data = " "
    # TODO 20200915-08 urlopen 如果需要取值，也需要 decode('ascii') bytes to string
    data = urllib2.urlopen(HOSTURL).read().decode("ascii").split()
    HOSTindex = data.index("Cisco")
    HOST = data[HOSTindex - 11].rstrip('</td>')
    print("HOST is %s" % HOST)

    SNURL = "http://%s/common/getTableData.cgi?SYS_ABOUT" % (IP)
    # TODO 20200915-08
    SN = urllib2.urlopen(SNURL).read().decode("ascii")
    print("SN is %s" % (SN))

    URL = "http://%s" % (IP)
    PICFOLDER = "%s/alarms.png" % (RFFOLDER)
    browser.get(URL)
    time.sleep(2)
    elem = browser.find_element_by_id("menu-alarms")
    elem.click()
    time.sleep(2)
    print("PICFOLDER1", PICFOLDER)
    browser.get_screenshot_as_file(PICFOLDER)

    URL = "http://%s/fs/Summary_noappl.htm" % (IP)
    PICFOLDER = "%s/Summary_noappl.png" % (RFFOLDER)
    browser.get(URL)
    elem = browser.find_element_by_id("bandwidth")
    elem.click()
    browser.execute_script("document.body.style.zoom='60%'")
    time.sleep(4)
    print("PICFOLDER2", PICFOLDER)
    browser.get_screenshot_as_file(PICFOLDER)

    URL = "http://%s/fs/Inventory.html" % (IP)
    PICFOLDER = "%s/Inventory.png" % (RFFOLDER)
    browser.get(URL)
    time.sleep(2)
    print("PICFOLDER3", PICFOLDER)
    browser.get_screenshot_as_file(PICFOLDER)

    URL = "http://%s/fs/resource_utilization.htm" % (IP)
    PICFOLDER = "%s/resource_utilization.png" % (RFFOLDER)
    browser.get(URL)
    time.sleep(2)
    print("PICFOLDER4", PICFOLDER)
    browser.get_screenshot_as_file(PICFOLDER)

    URL = "http://%s/fs/about.html" % (IP)
    PICFOLDER = "%s/about.png" % (RFFOLDER)
    browser.get(URL)
    time.sleep(2)
    print("PICFOLDER5", PICFOLDER)
    browser.get_screenshot_as_file(PICFOLDER)

    URL = "http://%s/fs/temperature.html" % (IP)
    PICFOLDER = "%s/temperature.png" % (RFFOLDER)
    browser.get(URL)
    elem = browser.find_element_by_id("TempInF")
    elem.click()
    time.sleep(2)
    print("PICFOLDER6", PICFOLDER)
    browser.get_screenshot_as_file(PICFOLDER)

    URL = "http://%s/fs/Global_qam96_port_channel.htm" % (IP)
    PICFOLDER = "%s/Global_qam96_port_channel.png" % (RFFOLDER)
    browser.get(URL)
    browser.execute_script("document.body.style.zoom='70%'")
    time.sleep(2)
    print("PICFOLDER7", PICFOLDER)
    browser.get_screenshot_as_file(PICFOLDER)

    URL = "http://%s/fs/ip_config.htm" % (IP)
    PICFOLDER = "%s/ip_config.png" % (RFFOLDER)
    browser.get(URL)
    time.sleep(2)
    print("PICFOLDER8", PICFOLDER)
    browser.get_screenshot_as_file(PICFOLDER)

    URL = "http://%s/log/logmgr.cgi?mode=SAVE" % (IP)
    LOGFOLDER = "%s/%s_%s.txt" % (RFFOLDER, SN, HOST)
    output = urllib2.urlopen(URL)
    fp = open(LOGFOLDER, "wb")
    fp.write(output.read())

    browser.close()
    browser.quit()


def allow_flash(driver, url):
    def _base_url(url):
        if url.find("://") == -1:
            url = "http://{}".format(url)
        urls = urlsplit(url)
        return "{}://{}".format(urls.scheme, urls.netloc)

    def _shadow_root(driver, element):
        return driver.execute_script("return arguments[0].shadowRoot", element)

    base_url = _base_url(url)
    driver.get("chrome://settings/content/siteDetails?site={}".format(url_quoteplus(base_url)))

    root1 = driver.find_element(WebBy.TAG_NAME, "settings-ui")
    shadow_root1 = _shadow_root(driver, root1)
    root2 = shadow_root1.find_element(WebBy.ID, "container")
    root3 = root2.find_element(WebBy.ID, "main")
    shadow_root3 = _shadow_root(driver, root3)
    root4 = shadow_root3.find_element(WebBy.CLASS_NAME, "showing-subpage")
    shadow_root4 = _shadow_root(driver, root4)
    root5 = shadow_root4.find_element(WebBy.ID, "basicPage")
    root6 = root5.find_element(WebBy.TAG_NAME, "settings-privacy-page")
    shadow_root6 = _shadow_root(driver, root6)
    root7 = shadow_root6.find_element(WebBy.ID, "pages")
    root8 = root7.find_element(WebBy.TAG_NAME, "settings-subpage")
    root9 = root8.find_element(WebBy.TAG_NAME, "site-details")
    shadow_root9 = _shadow_root(driver, root9)
    root10 = shadow_root9.find_element(WebBy.ID, "plugins")  # Flash
    shadow_root10 = _shadow_root(driver, root10)
    root11 = shadow_root10.find_element(WebBy.ID, "permission")
    WebSelect(root11).select_by_value("allow")
    root10a = shadow_root9.find_element(WebBy.ID, "popups")  # 彈出式視窗與重新導向
    shadow_root10a = _shadow_root(driver, root10a)
    root11a = shadow_root10a.find_element(WebBy.ID, "permission")
    WebSelect(root11a).select_by_value("allow")


def get_pnr_http_screenshot(IP, HOST, SO, DEVICE, id, pw):
    chromedriver = "chromedriver/chromedriver.exe"
    options = webdriver.ChromeOptions()
    # options.binary_location = "c:\myproject\chromeportable\chrome.exe"
    options.add_argument('ignore-certificate-errors')
    options.add_argument('--allow-outdated-plugins')

    prefs = {
        "profile.managed_default_content_settings.images": 1,
        "profile.default_content_setting_values.plugins": 1,
        "profile.content_settings.plugin_whitelist.adobe-flash-player": 1,
        "profile.content_settings.exceptions.plugins.*,*.per_resource.adobe-flash-player": 1
    }

    # png_folder = "LOG/%s/%s/%s" % (DEVICE, SO, HOST)
    png_folder = "{}/{}/{}/{}".format(str_log, DEVICE, SO, HOST)
    print("png_folder:", png_folder)
    if not os.path.exists(png_folder):
        os.makedirs(png_folder)
    png_file_name = "{}({}).png".format(HOST, IP)
    png_file_full_path = os.path.join(png_folder, png_file_name)
    options.add_experimental_option("prefs", prefs)
    browser = webdriver.Chrome(chromedriver, chrome_options=options)
    url = "https://{ip}/login.html".format(ip=IP)
    print("url:", url)
    allow_flash(browser, url)
    browser.get(url)
    browser.maximize_window()
    elem = browser.find_element_by_id("username")
    elem.send_keys(id)
    elem = browser.find_element_by_id("password")
    elem.send_keys(pw)
    elem = browser.find_element_by_id("cuesLoginSubmitButton")
    elem.click()
    time.sleep(20)
    # driver.save_screenshot("pnr{ip}.png".format(ip=ip))
    browser.get_screenshot_as_file(png_file_full_path)
    browser.close()


def get_adobe_screenshot(IP, HOST, SO, DEVICE, id, pw):
    chromedriver = "GoogleChromePortable86/chromedriver81.exe"
    options = webdriver.ChromeOptions()
    options.binary_location = "GoogleChromePortable86/GoogleChromePortable81.exe"
    # options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('ignore-certificate-errors')
    options.add_argument('--allow-outdated-plugins')

    prefs = {
        "profile.managed_default_content_settings.images": 1,
        "profile.default_content_setting_values.plugins": 1,
        "profile.content_settings.plugin_whitelist.adobe-flash-player": 1,
        "profile.content_settings.exceptions.plugins.*,*.per_resource.adobe-flash-player": 1
    }

    # png_folder = "LOG/%s/%s/%s" % (DEVICE, SO, HOST)
    png_folder = "{}/{}/{}/{}".format(str_log, DEVICE, SO, HOST)
    print("png_folder:", png_folder)
    if not os.path.exists(png_folder):
        os.makedirs(png_folder)
    png_file_name = "{}({}).png".format(HOST, IP)
    png_file_full_path = os.path.join(png_folder, png_file_name)
    # options.add_experimental_option("prefs", prefs)
    browser = webdriver.Chrome(chromedriver, chrome_options=options)
    url = "http://{ip}/login.html".format(ip=IP)
    print("url:", url)
    allow_flash(browser, url)
    browser.get(url)
    browser.maximize_window()
    elem = browser.find_element_by_id("username")
    elem.send_keys(id)
    elem = browser.find_element_by_id("password")
    elem.send_keys(pw)
    elem = browser.find_element_by_id("cuesLoginSubmitButton")
    elem.click()
    time.sleep(20)
    # driver.save_screenshot("pnr{ip}.png".format(ip=ip))
    browser.get_screenshot_as_file(png_file_full_path)
    browser.close()



