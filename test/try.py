# !/usr/bin/python
# -*- coding: utf-8 -*-
import time

from DrissionPage import ChromiumPage, ChromiumOptions
from DrissionPage.common import configs_to_here

configs_to_here()


class DYComments:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.chrome_option = ChromiumOptions()

    def add_chrome_option(self, browser_path):
        # self.chrome_option.set_headless(True)
        # self.chrome_option.set_proxy('http://localhost:10808')
        # self.chrome_option.set_paths(browser_path=r'd:\Downloads\Win_1230979_chrome-win\chrome-win\chrome.exe')
        # self.chrome_option.set_paths(browser_path=r'C:\Users\Administrator\Desktop\git_project\chrome.exe')
        if browser_path:
            self.chrome_option.set_paths(browser_path=browser_path)
        self.chrome_option.auto_port()

    def start_chrome(self, key_word):
        # self.add_chrome_option()
        page = ChromiumPage(addr_or_opts=self.chrome_option)
        page.get(f'https://news.baidu.com/')

        tab_detail = page.new_tab()
        tab_detail.get(f'https://www.baidu.com/')
        # page.wait.load_start()
        # page.wait.ele_displayed('xpath://*[@id="island_b69f5"]/div/div[last()]/div/a', timeout=120)  # 等待登录

        # cookies = page.get_cookies(as_dict=True)
        # print(cookies)

        print(type(page))
        print(type(tab_detail))
        time.sleep(3)
        page.scroll.to_bottom()

        # print(type(page))
        # while True:
        #     page.scroll.down(pixel=120)
        #     time.sleep(10)

        # # return
        # print(22222)
        # for ul in page.eles('xpath://*[@id="pane-news"]/div/ul'):
        #     print(111111)
        #     ul.scroll.to_bottom()
        #     page.wait.load_start()
        #     break
        #
        # time.sleep(10)
        # print(f'123: {page.states.is_alive}')
        # page.quit()
        # print(f'234: {page.states.is_alive}')
        # page.set.cookies.clear()
        #
        #
        # print(11111)
        # print('page: ', page)
        # aa = page.ele('xpath://header', timeout=3).text
        # print(aa)
        # print(22222)

if __name__ == '__main__':
    DYComments().start_chrome('医美')


