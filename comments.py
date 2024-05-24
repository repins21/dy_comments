# !/usr/bin/python
# -*- coding: utf-8 -*-
import os
import re
import time
import json
from typing import Callable, Optional
from datetime import datetime

import DrissionPage
import DrissionPage.errors
from DrissionPage import ChromiumPage, ChromiumOptions

from exceptions import StopCrawler
from db.operate_db import insert, get_max_search_id


class DYComments:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, stop_crawler_or_not: Callable[[], bool]):
        self.new_search_id: Optional[str] = None
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

    def get_data(self, search_info: str, browser_path: Optional[str] = None, filter_condition: Optional[dict] = None):
        """
        :param search_info: 搜索内容
        :param browser_path: 浏览器路径（windows不用指定）
        :param filter_condition: 视频筛选条件
        :return:
        """
        self.new_search_id = get_max_search_id()

        if '复制打开抖音' in search_info:
            reg = '(https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]'
            srh = re.compile(reg).search(search_info)
            if srh:
                video_link = srh.group()
                yield from self.video_link_search(
                    search_info=search_info, video_link=video_link, browser_path=browser_path)
            else:
                yield {'code': 1, 'msg': '没有匹配到视频链接'}
        elif search_info.startswith('https://www.douyin.com/video/'):
            yield from self.video_link_search(
                search_info=search_info, video_link=search_info, browser_path=browser_path)
        else:
            yield from self.keyword_search(
                search_info=search_info, browser_path=browser_path, filter_condition=filter_condition)

    def keyword_search(
            self,
            search_info: Optional[str],
            browser_path: Optional[str] = None,
            filter_condition: Optional[dict] = None
    ):
        """
        关键词搜索
        :param search_info:
        :param browser_path: 浏览器路径
        :param filter_condition: 视频筛选条件
        :return:
        """
        url = f'https://www.douyin.com/search/{search_info}?type=video'

        page = self.start_chrome(browser_path)
        page.listen.start(['/search/item/'])
        page.get(url, timeout=5)
        while True:
            self._whether_stop(page)
            try:
                # 检查是否登录
                if '退出登录' in page.ele('xpath://header', timeout=3).text:
                    cookies = page.cookies(as_dict=True, all_info=True)
                    cookies.update({'domain': 'www.douyin.com'})
                    self.save_cookies(cookies)
                    break
            except DrissionPage.errors.ElementNotFoundError as e:
                # 有时候会弹出验证码
                time.sleep(3)

        page.wait.load_start()

        if filter_condition:
            self.filter_video(page, filter_condition)

        for packet in page.listen.steps(timeout=3):
            self._whether_stop(page)
            if '/search/item/' in packet.url:
                if filter_condition:
                    # 通过频繁点击筛选条件，查看接口参数情况，得出：
                    # 只要有筛选条件，那么最后点击的都是“搜索范围”，此时的接口上才会出现参数search_range，以此判断我们需要的接口
                    if 'search_range' in packet.url:
                        pass
                    else:
                        continue
                json_data = packet.response.body
                for item in json_data.get('data', {}):  # 遍历每个视频
                    self._whether_stop(page)
                    video_data = self.extract_video_data(search_info=search_info, data=item)

                    video_id = video_data['video_id']
                    if video_id:
                        video_link = f'https://www.douyin.com/video/{video_id}'
                        yield from self.crawl_video_comments(
                            search_info=search_info, page=page, video_link=video_link, video_data=video_data)

                has_more = json_data.get('has_more')
                if not has_more:
                    break

            page.scroll.to_bottom()  # 下一页
            time.sleep(2)

        self._quit(page)

    @staticmethod
    def filter_video(page: DrissionPage._pages.chromium_page.ChromiumPage,  # noqa
                     filter_condition: dict):
        """
        模拟点击视频筛选条件
        """

        # 都是序号
        sort_type = filter_condition["sort_type"]
        publish_time = filter_condition["publish_time"]
        filter_duration = filter_condition["filter_duration"]
        search_range = filter_condition["search_range"]
        # 移动鼠标
        page.actions.move_to('xpath://*[@id="search-content-area"]/div/div[1]/div[1]/div[1]/div[2]/div/span')
        # 点击筛选条件
        page.ele(
            f'xpath://*[@id="search-content-area"]/div/div[1]/div[1]/div[1]/div[2]/div/div/div[1]/span[{sort_type+1}]').click()
        time.sleep(0.5)
        page.ele(
            f'xpath://*[@id="search-content-area"]/div/div[1]/div[1]/div[1]/div[2]/div/div/div[2]/span[{publish_time+1}]').click()
        time.sleep(0.5)
        page.ele(
            f'xpath://*[@id="search-content-area"]/div/div[1]/div[1]/div[1]/div[2]/div/div/div[3]/span[{filter_duration+1}]').click()
        time.sleep(0.5)
        page.ele(
            f'xpath://*[@id="search-content-area"]/div/div[1]/div[1]/div[1]/div[2]/div/div/div[4]/span[{search_range+1}]').click()
        time.sleep(1)

    def video_link_search(self, search_info: str, video_link: Optional[str], browser_path: Optional[str] = None):
        """
        视频链接搜索
        :param search_info:
        :param video_link:
        :param browser_path: 浏览器路径
        :return:
        """

        page = self.start_chrome(browser_path)
        page.listen.start(['aweme/detail/', 'comment/list/'])
        page.get(video_link, timeout=5)
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

        # page.wait.load_start()

        yield from self.crawl_video_comments(search_info=search_info, page=page)
        self._quit(page)

    def crawl_video_comments(
            self,
            search_info: str,
            page: DrissionPage._pages.chromium_page.ChromiumPage, # noqa
            video_link: Optional[str] = None,
            video_data: Optional[dict] = None
    ):
        """
        请求视频链接，监听评论接口
        """

        if video_link:
            page_detail = page.new_tab()
            page_detail.listen.start(['comment/list/'])
            page_detail.get(video_link, timeout=5)
        else:
            page_detail = page

        video_comments_data = []
        for packet in page_detail.listen.steps(timeout=3):
            self._whether_stop(page_detail)

            if 'aweme/detail/' in packet.url:  # 直接搜索视频的情况
                json_data = packet.response.body
                video_data = self.extract_video_data(search_info=search_info, data=json_data)

            if 'comment/list/' in packet.url:
                json_data = packet.response.body
                comment_data, has_more = self.extract_comment_data(video_id=video_data['video_id'], data=json_data)
                video_comments_data += comment_data

                if len(video_comments_data) >= 20 or (not has_more and len(video_comments_data) < 20):
                    yield {
                        'code': 0,
                        'msg': 'ok',
                        'data': {
                            'video_info': video_data or {},
                            'comments_info': video_comments_data
                        },
                        'has_more': has_more,
                        'all_finish': 0
                    }
                    video_comments_data.clear()

                if not has_more:
                    if video_link:
                        page_detail.close()  # 关闭标签页，防止无限打开新标签页
                    break

                page_detail.scroll.down(pixel=120)

    def extract_video_data(self, search_info: str, data: dict):
        """提取视频数据"""
        aweme_info = data.get('aweme_info', {}) or data.get('aweme_detail', {})

        aweme_id = aweme_info.get('aweme_id')

        author = aweme_info.get('author', {})
        author_name = author.get('nickname', '')

        title = aweme_info.get('desc', '')

        video_publish_time = aweme_info.get('create_time', 0)
        video_publish_time = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(video_publish_time)) if video_publish_time else video_publish_time

        statistics = aweme_info.get('statistics', {})
        collect_count = statistics.get('collect_count', 0)  # 收藏数
        comment_count = statistics.get('comment_count', 0)  # 评论数
        digg_count = statistics.get('digg_count', 0)  # 点赞数
        share_count = statistics.get('share_count', 0)  # 分享数

        video = aweme_info.get('video', {})
        duration = round(video.get('duration', 0) / 1000)  # 时长: s

        video_data = {
            'video_id': aweme_id,
            'title': title,
            'author_name': author_name,
            'video_publish_time': video_publish_time,
            'duration': duration,
            'collect_count': collect_count,
            'comment_count': comment_count,
            'digg_count': digg_count,
            'share_count': share_count
        }

        insert(table_name='search_history', data={
            'id': self.new_search_id,
            'search': search_info,
            'video_id': aweme_id,
            'datetime': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        insert(table_name='video_info', data={
            'video_id': aweme_id,
            'search_id': self.new_search_id,
            'title': title,
            'author_name': author_name,
            'video_publish_time': video_publish_time,
            'duration': duration,
            'collect_count': collect_count,
            'comment_count': comment_count,
            'digg_count': digg_count,
            'share_count': share_count
        })

        return video_data

    @staticmethod
    def extract_comment_data(video_id: str, data: dict):
        """提取评论数据"""
        comment_data = []
        comments = data.get('comments') or []  # 有这种情况：有此key，但为None （新发布的视频，还没有人评论）
        for item in comments:
            user = item.get('user', {})
            uid = user.get('uid')
            user_name = user.get('nickname')

            sec_uid = user.get('sec_uid')
            homepage_link = 'https://www.douyin.com/user/' + sec_uid if sec_uid else None

            comment_time = item.get('create_time')
            comment_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(comment_time)) if comment_time else comment_time

            ip_address = item.get('ip_label')
            comment_text = item.get('text')

            comment_data.append({
                'uid': uid,
                'user_name': user_name,
                'comment_time': comment_time,
                'comment_text': comment_text,
                'ip_address': ip_address,
                'homepage_link': homepage_link
            })

            insert(table_name='users', data={
                'uid': uid,
                'video_id': video_id,
                'user_name': user_name,
                'homepage_link': homepage_link,
                'has_letter': 0
            })

            insert(table_name='comments', data={
                'uid': uid,
                'ip_address': ip_address,
                'comment_time': comment_time,
                'comment_text': comment_text
            })

        has_more = data.get('has_more')
        return comment_data, has_more

    def _whether_stop(self, page: DrissionPage._pages.chromium_page.ChromiumPage):  # noqa
        """是否停止"""
        if self.stop_crawler_or_not():
            self._quit(page)
            raise StopCrawler('手动停止爬取')

        if not page.states.is_alive:
            self._quit(page)
            raise StopCrawler('网页被关闭')

    def _quit(self, page: DrissionPage._pages.chromium_page.ChromiumPage):  # noqa
        page.set.cookies.clear()
        page.quit()


if __name__ == '__main__':
    generator11 = DYComments().get_data(search_info='https://www.douyin.com/video/7360327123862588723', browser_path=None)
    if isinstance(generator11, dict):
        print(generator11)
    else:
        try:
            while True:
                comments1 = next(generator11)
                print(comments1)
        except StopIteration:
            print('StopIteration')
