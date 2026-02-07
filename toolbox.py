'''
主要是要做一些基礎函數的工具箱

'''

import os
import configparser
import re
import ntplib

from datetime import datetime, timezone, timedelta
from inspect import currentframe

# TODO
# Do the log function to record the processes
def logger():
    return

def debug_print(*args, **kwargs):
    '''
    在執行介面輸出當下時間 <執行在哪個檔案> line 行數編號: 輸出的文字
    可以傳入任意字元或字串
    '''
    frame = currentframe().f_back
    filename = os.path.basename(frame.f_code.co_filename)
    line_num = frame.f_lineno
    msg = [str(arg) for arg in args]
    if kwargs:
        msg.append(str(kwargs))
    if not msg:
        msg = ''
    print(f"{round_time()} <{filename}> line {line_num}: {' '.join(msg)}")

def round_time():
    '''
    回傳當下的時間，符合: 年-月-日 時:分:秒.(三位毫秒)
    '''
    return datetime.fromtimestamp(round(datetime.now().timestamp(),3)).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

def date_split(date_str: str):
    '''
    將網頁上的時間切割開來，只留下年/月/日
    '''
    date_list = []
    if '~' in date_str:
        start_date, end_date = date_str.split('~')
        date_list.append(start_date.split('(')[0].strip())
        date_list.append(end_date.split('(')[0].strip())
    else:
        date_list.append(date_str.split('(')[0].strip())
    return date_list

def config_reader(filename = 'Arguments.ini'):
    '''
    讀取ini檔案並轉成dict的樣式，預設讀取Arguments.ini
    '''
    if not os.path.exists(filename):
        debug_print(f'{filename} does not exists.')
    config = configparser.ConfigParser()
    config.read(filename, encoding = 'UTF-8')
    return {section: dict(config[section]) for section in config.sections()}

def parse_date_to_timestamp(date_str):
    
    # 定義正規表示式
    # (?:(\d{3,4})/)?  -> Group 1: 3到4位數的年份 (可選)，例如 2026 或 026
    # (\d{1,2})        -> Group 2: 1到2位數的月份
    # /                -> 分隔符號
    # (\d{1,2})        -> Group 3: 1到2位數的日期
    date_pattern = re.compile(r"(?:(\d{3,4})/)?(\d{1,2})/(\d{1,2})")

        # 去除前後空白與換行，方便閱讀 log
    clean_text = date_str.strip()
    
    # 在字串中尋找所有符合日期的模式
    matches = date_pattern.finditer(clean_text)
    
    timestamps = []
    readable_dates = []

    # 如果輸入的時間是xxx~xxx的話還可以使用
    for match in matches:
        year_str, month_str, day_str = match.groups()

        # 1. 處理年份
        if year_str:
            year = int(year_str)
            # 處理 typo: 如果是 '026' 這種小於 100 的數字，修正為當下的年份
            if year < 100:
                year = int(get_ntp_time()[:4])
            # 處理民國年的問題
            elif 100 <= year <= 1000:
                year += 1911
        else:
            year = int(get_ntp_time()[:4])

        month = int(month_str)
        day = int(day_str)

        try:
            # 2. 建立 datetime 物件
            # 預設時間為 00:00:00 (即題目中的 "零時")
            dt = datetime(year, month, day)
            
            # 3. 轉成 Timestamp (float)
            ts = dt.timestamp()
            
            timestamps.append(ts)
            readable_dates.append(dt.strftime("%Y-%m-%d %H:%M:%S"))
            
        except Exception as e:
            debug_print(f'Parse date error: {e}')

    res = {
        "source_date": clean_text.replace('\n', ' '), # 為了顯示整潔把換行拿掉
        "timestamps": timestamps,
        "readable_date": readable_dates
    }
            
    return res

def get_ntp_time():
    '''
    return format: (datetime(2026-01-31 23:36:51.942642+08:00), utc current timestamp)
    '''
    try:
        client = ntplib.NTPClient()
        # 連線到台灣的 NTP 伺服器池，如果連不上可改用 pool.ntp.org
        response = client.request('tw.pool.ntp.org', version=3)
        
        # NTP 回傳的是 UTC 的 timestamp
        utc_timestamp = response.tx_time
        
        # 手動設定時區為 UTC+8
        tz_taipei = timezone(timedelta(hours=8))
        dt = datetime.fromtimestamp(utc_timestamp, tz_taipei)

        
    except Exception as e:
        raise ValueError("NTP Fail. Please check NTP server pool link.")
    
    return dt, int(utc_timestamp)
    

if __name__ == '__main__':
    print(parse_date_to_timestamp('2026/05/08 (五) ~ 2026/05/11 (一)'))
    print(get_ntp_time())