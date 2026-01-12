'''
主要是要做一些基礎函數的工具箱，例如日期字串分割或是debug 用的 print 函數

'''

import os

from inspect import currentframe

def debug_print(msg):
    frame = currentframe().f_back
    filename = os.path.basename(frame.f_code.co_filename)
    line_num = frame.f_lineno
    print(f"<{filename}> line {line_num}: {msg}")

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
    debug_print(date_split('2026/04/02 (四) ~ 2026/04/07 (二)'))