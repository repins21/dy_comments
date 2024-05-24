# !/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time
import json
import random
from typing import Callable, Optional

import DrissionPage
import DrissionPage.errors
from DrissionPage import ChromiumPage, ChromiumOptions
from exceptions import StopCrawler


class HomePage:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, stop_crawler_or_not: Callable[[], bool]):
        self.chrome_option = ChromiumOptions()
        self.stop_crawler_or_not = stop_crawler_or_not

    def add_chrome_option(self, browser_path):
        if browser_path:
            self.chrome_option.set_paths(browser_path=browser_path)
        # self.chrome_option.auto_port()  # 会新开一个端口，不会接管已经打开的浏览器

    @staticmethod
    def get_cookies():
        if os.path.exists('cookies.json'):
            with open('cookies.json', 'r', encoding='utf-8') as f:
                string = f.read()
                if string:
                    cookies = json.loads(string)
                    return cookies

    @staticmethod
    def save_cookies(cookies: dict):
        if cookies:
            with open('cookies.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(cookies))

    def start_chrome(self, browser_path):
        self.add_chrome_option(browser_path=browser_path)
        page = ChromiumPage(addr_or_opts=self.chrome_option)

        cookies = self.get_cookies()
        if cookies:
            page.set.cookies(cookies)

        return page

    def check_login(self, page: DrissionPage._pages.chromium_page.ChromiumPage):  # noqa
        """检查登录状态"""
        while True:
            self._whether_stop(page)
            try:
                # 检查是否登录
                if '退出登录' in page.ele('xpath://header', timeout=3).text:
                    cookies = page.cookies(as_dict=True, all_info=True)
                    cookies.update({'domain': 'www.douyin.com'})
                    self.save_cookies(cookies)
                    break
            except DrissionPage.errors.ElementNotFoundError:
                # 有时候会弹出验证码
                time.sleep(3)

    def follow_send_msg(self, homepage_links: list, msg: str, browser_path: Optional[str] = None):
        page = self.start_chrome(browser_path)
        for link_index, homepage_link in enumerate(homepage_links):
            self._whether_stop(page)

            if homepage_link.startswith('http'):
                page.get(homepage_link, timeout=5)

                if link_index == 0:  # 首次时，先检查登录
                    self.check_login(page)

                page.wait.load_start(timeout=3)
                follow_ele = page.ele(
                    'xpath://*[@id="douyin-right-container"]/div[2]/div/div/div[2]/div[3]/div[3]/div[1]/button[1]')
                if '已关注' in follow_ele.text:
                    pass
                else:
                    follow_ele.click(timeout=2)
                    time.sleep(1)
                send_msg_ele = page.ele(
                    'xpath://*[@id="douyin-right-container"]/div[2]/div/div/div[2]/div[3]/div[3]/div[1]/button[2]')
                if '私信' in send_msg_ele.text:
                    # 等待自己头像的左边的’私信‘出现，这时候点击私信才会弹出框
                    page.wait.eles_loaded('xpath://div[@data-e2e="im-entry"]')
                    send_msg_ele.click(timeout=2)
                    page.ele('xpath://div[@data-mask="conversaton-detail-input-content"]').input(msg)
                    page.ele(
                        'xpath://div[@data-mask="conversaton-detail-input-content"]/div/div/div[1]/div[2]/div/span[2]').click(timeout=1)

                time.sleep(random.randint(1, 2) + random.random())

        self._quit(page)

    def _whether_stop(self, page: DrissionPage._pages.chromium_page.ChromiumPage):  # noqa
        """是否停止"""
        if self.stop_crawler_or_not():
            self._quit(page)
            raise StopCrawler('手动停止爬取or激活码失效')

        if not page.states.is_alive:
            self._quit(page)
            raise StopCrawler('网页被关闭')

    def _quit(self, page: DrissionPage._pages.chromium_page.ChromiumPage):  # noqa
        page.set.cookies.clear()
        page.quit()


if __name__ == '__main__':
    def aa():
        return False
    HomePage(aa).follow_send_msg(
        ['https://www.douyin.com/user/MS4wLjABAAAAXkb5zHdLyUIF3pEM-jknAjr935yPoCKiGFublmbAW3iXynnWenN50ozy81qgLLd1'],
        '111'
    )
