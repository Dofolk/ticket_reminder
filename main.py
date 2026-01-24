import os
import re
import datetime
import win32com.client

from toolbox import *
from pprint import pprint
from collections import defaultdict
from playwright.sync_api import sync_playwright
from winotify import Notification, audio
from types import SimpleNamespace

configs = SimpleNamespace(**config_reader())
URLs = configs.URL if configs.URL else "https://www.thsrc.com.tw/ArticleContent/60dbfb79-ac20-4280-8ffb-b09e7c94f043"

def get_table_contents(url = URLs['thsr']):
    table = defaultdict(dict)
    fes_list = list()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print(f"正在連線至: {url} ...")
        page.goto(url)

        # 處理高鐵的part，因為高鐵的表格目前的規則比較嚴謹所以處理起來相對簡單
        if 'thsrc.com' in url:
            # 等待表格內容載入 (等待頁面中的 table 元素出現)
            try:
                page.wait_for_selector("table")
                debug_print("已找到表格，正在讀取資料...")
            except:
                debug_print("找不到表格。")
                pass

            # 取得網頁標題
            # title = page.title()
            # print(f"網頁標題: {title}\n")

            # 視覺化抓取：抓取表格中的所有列數據
            rows = page.locator("table tr").all()
            
            # print(f"{'假期名稱':<15} | {'疏運期間':<30} | {'開放預售日期'}")
            # print("-" * 70)

            for row in rows:
                # 取得每一列中所有儲存格的文字
                cols = row.locator("td").all_text_contents()
                if cols:
                    # 整理節日及對應的日期與購票時間
                    fes_name, duration, book_date = [c.strip() for c in cols]
                    fes_list.append(fes_name)
                    table[fes_name]['duration'] = duration
                    table[fes_name]['book_date'] = book_date
                    
                    # if len(data) >= 3:
                    #     print(f"{data[0]:<15} | {data[1]:<30} | {data[2]}")
        
        # 台鐵頁面比較複雜還會跨列，需要額外處理
        else:
            try:
            # 定位表格
                table_locator = page.locator("table", has=page.locator("text='假期名稱'"))
                table_locator.wait_for()
                debug_print("已找到表格，正在讀取資料...")
            except:
                debug_print("找不到表格。")
                pass

            rows = table_locator.locator("tr").all()
            row_span_prev = []
            table_col_num = 0
            title_mapping = {}
            row_span_count = 0

            for idx, row in enumerate(rows):
                # 抓取該列所有的格子 (包含 th 和 td)
                cells = row.locator("th, td").all()
                
                # 將每個格子的文字取出來，並去除多餘空白
                row_text = [cell.inner_text().strip() for cell in cells]
                row_span_prev = row_text
                
                # 第一列是標題，先記錄表格有幾個column之後就可以pass掉
                if idx == 0:
                    table_col_num = len(row_text)
                    continue
                
                # 開始處理表格內的資訊，先確認有沒有符合column數量
                # 接著對數量跟title數量相同的做簡單處理，把資訊都記錄好就可以了
                if len(row_text) == table_col_num:
                    fes_name, book_date, duration, _ = row_text
                    fes_list.append(fes_name)
                    table[fes_name]['duration'] = duration
                    table[fes_name]['book_date'] = book_date
                    row_span_count = 0
                # 當row 所含的column數量與title不合的時候就代表有共用column的內容
                # 這時候就把之前存好的節日名稱跟假期期間傳遞下來用就好了
                else:
                    try:
                        fes_name = row_span_prev[0]
                        book_date, duration = row_text # 這一步可以順便確認共用的是不是名稱跟期間，用兩個變數來做span
                        table[fes_name][f'duration{row_span_count + 1}'] = duration
                        table[fes_name][f'book_date{row_span_count + 1}'] = book_date
                        row_span_count += 1
                    except:
                        raise ValueError("row item number error")

        browser.close()
    return fes_list, table

def win_toast(fes_name, fes_contents, railway_name = "高鐵"):
    toast = Notification(
        app_id = f"{railway_name}搶票提醒",
        title = f"{railway_name}{fes_name}搶票提醒",
        msg = f"{fes_name}節日期間是:\n{fes_contents['duration']}\n搶票日期:\n{fes_contents['book_date']}",
        duration = "short"
    )
    return toast

if __name__ == "__main__":
    # fes_list, table_contents = get_table_contents()
    # toast = win_toast(fes_list[0], table_contents[fes_list[0]])
    thsr_fes, thsr_table = get_table_contents(URLs['thsr'])
    tr_fes, tr_table = get_table_contents(URLs['tr'])
    print(thsr_table, tr_table)