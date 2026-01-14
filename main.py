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

fes_list = list()
configs = SimpleNamespace(**config_reader())
URLs = configs.URL if configs.URL else "https://www.thsrc.com.tw/ArticleContent/60dbfb79-ac20-4280-8ffb-b09e7c94f043"

def get_table_contents(url = URLs['thsr']):
    table = defaultdict(dict)
    global fes_list
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print(f"正在連線至: {url} ...")
        page.goto(url)

        if 'thsr' in url:
            # 等待表格內容載入 (等待頁面中的 table 元素出現)
            page.wait_for_selector("table")

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
        else:
            try:
            # 定位表格
                table_locator = page.locator("table", has=page.locator("text='假期名稱'"))
                table_locator.wait_for()
                print("已找到表格，正在讀取資料...")
            except:
                print("找不到表格。")
                browser.close()
                return

        rows = table_locator.locator("tr").all()
        
        table_data = []
        headers = []

        for i, row in enumerate(rows):
            # 抓取該列所有的格子 (包含 th 和 td)
            cells = row.locator("th, td").all()
            
            # 將每個格子的文字取出來，並去除多餘空白
            row_text = [cell.inner_text().strip() for cell in cells]
            
            # 第一列是標題
            if i == 0:
                headers = row_text
            else:
                if row_text:
                    table_data.append(row_text)
        print(headers, table_data)

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
    # debug_print(toast.show())
    print(get_table_contents(URLs['tr']))