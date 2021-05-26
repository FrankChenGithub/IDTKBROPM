import os

from selenium import webdriver
import sys
import traceback
from pythonping import ping
import datetime

chrome_driver_download_url = r"https://chromedriver.chromium.org/downloads"
chromedriver_loc = r"./chromedriver/chromedriver.exe"

def check_gateway_ip_availability():
    internet_ip = "8.8.8.8"
    kbro_vpn_gateway_ip = "10.222.120.254"
    response = ping(kbro_vpn_gateway_ip, count=3)
    print(response)
    if response.success:
        # print(response.rtt_avg_ms)
        rl = response._responses
        str_rl = ",".join(map(str, rl))
        if str_rl.find("timed out") > -1:
            # print(rl)
            return [False, "連線 VPN gateway 出現要求等候逾時(time out)錯誤"]
        else:
            return [True, response.rtt_avg_ms]


def check_chromedriver_version(driver_path):
    if driver_path == "":
        driver_path = chromedriver_loc
        # r"./chromedriver/chromedriver.exe"
    if not os.path.exists(driver_path):
        return ["NOEXE", driver_path + "不存在，請確認檔名及路徑，或下載更新"]

    try:
        msg = "因你系統的chrome瀏覽器版本{}與PM程式使用的chromedriver版本{}不匹配\n"
        msg = msg + "PM應用程式無法擷取網頁畫面\n"
        msg = msg + "請至{}下載適合的chromedriver版本進行替換"
        driver = webdriver.Chrome(driver_path)
        str1 = driver.capabilities['browserVersion']
        str2 = driver.capabilities['chrome']['chromedriverVersion'].split(' ')[0]
        print(str1)
        print(str2)
        print(str1[0:2])
        print(str2[0:2])
        if str1[0:2] != str2[0:2]:
            print("please download correct chromedriver version")
        driver.close()
        return ["OK", "OK"]
    except Exception as e:
        #    print(e)
        error_class = e.__class__.__name__  # 取得錯誤類型
        detail = e.args[0]  # 取得詳細內容
        cl, exc, tb = sys.exc_info()  # 取得Call Stack
        lastCallStack = traceback.extract_tb(tb)[-1]  # 取得Call Stack的最後一筆資料
        # fileName = lastCallStack[0]  # 取得發生的檔案名稱
        # lineNum = lastCallStack[1]  # 取得發生的行號
        # funcName = lastCallStack[2]  # 取得發生的函數名稱
        # print("detail:", detail)
        # print()
        # print("cl:", cl)
        # print()
        # print("exc:", exc)
        # print()
        # print("tb:", tb)
        # print()
        # print("lastCallStack:", lastCallStack)
        dd = detail.split()
        indices = [i for i, x in enumerate(dd) if x == "version"]
        for idx in indices:
            if idx-1 > 0:
                if dd[idx-1] == "browser":
                    browser_version = dd[idx+2]
                elif dd[idx-1] == "Chrome":
                    driver_version = dd[idx+1]
        msg = msg.format(browser_version, driver_version, chrome_driver_download_url)
        return ["WRONGVERSION", msg]


if __name__ == "__main__":
    t_start = datetime.datetime.now()
    [result, message] = check_gateway_ip_availability()
    t_end = datetime.datetime.now()
    print("pinging gateway_ip: ", result, message)
    print(t_start)
    print(t_end)
    checked = check_chromedriver_version(chromedriver_loc)
    if checked == "OK":
        print("checked")
    else:
        print(checked)
