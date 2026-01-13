'''
主要是要做一些基礎函數的工具箱，例如日期字串分割或是debug 用的 print 函數

'''

import os

from datetime import datetime
from inspect import currentframe

def debug_print(*args, **kwargs):
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
    return datetime.fromtimestamp(round(datetime.now().timestamp(),3)).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

def date_split(date_str: str):
    date_list = []
    if '~' in date_str:
        start_date, end_date = date_str.split('~')
        date_list.append(start_date.split('(')[0].strip())
        date_list.append(end_date.split('(')[0].strip())
    else:
        date_list.append(date_str.split('(')[0].strip())
    return date_list

if __name__ == '__main__':
    debug_print(round_time())
    #debug_print(date_split('2026/04/02 (四) ~ 2026/04/07 (二)'))