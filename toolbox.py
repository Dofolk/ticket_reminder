'''
主要是要做一些基礎函數的工具箱

'''

import os
import configparser

from datetime import datetime
from inspect import currentframe

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

if __name__ == '__main__':
    debug_print(config_reader())
    #debug_print(date_split('2026/04/02 (四) ~ 2026/04/07 (二)'))