import socket
import threading
import time
from collections.abc import Generator
from typing import Optional

import DrissionPage.errors
from flask import Flask, request, jsonify
from flask_cors import CORS
from gevent import pywsgi

from comments import DYComments
from home_page import HomePage
from utils import verify_activation_code
from exceptions import StopCrawler
from db import cloud_storage


app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False  # 支持中文
app.config['timeout'] = 20  # 所有请求必须在规定时间内完成，否则超时
CORS(app, supports_credentials=True)  # 跨域问题：前端和后端都要配置允许跨域

refresh_generator = True  # 刷新生成器
cmt_generator: Optional[Generator] = None
activation_code = None  # 激活码
activation_code_status = False  # 激活码状态
stop_crawler: bool = False  # 是否停止爬取


def stop_crawler_or_not() -> bool:
    """是否停止爬取"""
    global stop_crawler
    return stop_crawler


def data_generator():
    search_info = request.values.get("search_info")
    browser_path = request.values.get("browser_path")

    sort_type = request.values.get("sort_type")
    publish_time = request.values.get("publish_time")
    filter_duration = request.values.get("filter_duration")
    search_range = request.values.get("search_range")

    sort_type = int(sort_type) if sort_type else 0
    publish_time = int(publish_time) if publish_time else 0
    filter_duration = int(filter_duration) if filter_duration else 0
    search_range = int(search_range) if search_range else 0

    if sort_type == 0 and publish_time == 0 and filter_duration == 0 and search_range == 0:
        filter_condition = None
    else:
        filter_condition = {
            'sort_type': sort_type,
            'publish_time': publish_time,
            'filter_duration': filter_duration,
            'search_range': search_range
        }

    yield from DYComments(stop_crawler_or_not).get_data(
        search_info=search_info,
        browser_path=browser_path,
        filter_condition=filter_condition
    )


@app.route("/have_service", methods=["GET"])
def have_service():
    """服务是否启动"""
    return jsonify({'code': 0, "msg": "服务已启动"})


@app.route("/stop_crawler", methods=["GET"])
def stop_crawler_route():
    global stop_crawler
    stop_crawler = True
    return jsonify({'code': 0, "msg": "停止爬取请求已接收"})


@app.route('/get_comments', methods=['POST'])
def get_comments():
    global refresh_generator, cmt_generator, stop_crawler, activation_code_status

    activation_code_status = verify_activation_code(activation_code)
    if not activation_code_status:
        stop_crawler = True
        return jsonify({'code': 3, 'msg': '激活码无效',
                        'activation_code_status': activation_code_status})

    if refresh_generator:
        stop_crawler = False
        cmt_generator = data_generator()
        refresh_generator = False

    try:
        comments = next(cmt_generator)
        comments.update({'activation_code_status': activation_code_status})
        if comments.get('code') != 0:
            refresh_generator = True
        return jsonify(comments)
    except StopIteration:
        refresh_generator = True
        return jsonify({'code': 0, 'msg': 'ok', 'data': {}, 'has_more': 0, 'all_finish': 1,
                        'activation_code_status': activation_code_status})
    except DrissionPage.errors.PageDisconnectedError:
        refresh_generator = True
        return jsonify({'code': 2, 'msg': '与页面的连接已断开',
                        'activation_code_status': activation_code_status})
    except StopCrawler as e:
        refresh_generator = True
        return jsonify({'code': 4, 'msg': repr(e),
                        'activation_code_status': activation_code_status})


@app.route('/follow_send_msg', methods=['POST'])
def _follow_send_msg():
    global stop_crawler, activation_code_status
    stop_crawler = False

    json_data = request.get_json()
    msg = json_data.get('msg', '')
    video_info = json_data.get('data', {})

    homepage_links = []  # 关注+私信的
    comments_to_cloud = []  # 发送给云端的
    for video_link, homepage_info in video_info.items():
        for homepage_link, comments_list in homepage_info.items():
            homepage_links.append(homepage_link)
            for comment in comments_list:
                comments_to_cloud.append({
                    'comment': comment,
                    'homepageLink': homepage_link
                })

    cloud_storage.save(comments_to_cloud)

    activation_code_status = verify_activation_code(activation_code)
    if not activation_code_status:
        stop_crawler = True
        return jsonify({'code': 3, 'msg': '激活码无效',
                        'activation_code_status': activation_code_status})

    try:
        HomePage(stop_crawler_or_not).follow_send_msg(
            homepage_links=homepage_links,
            msg=msg
        )
        return jsonify({'code': 0, 'msg': 'ok',
                        'activation_code_status': activation_code_status})
    except DrissionPage.errors.PageDisconnectedError:
        return jsonify({'code': 2, 'msg': '与页面的连接已断开',
                        'activation_code_status': activation_code_status})
    except StopCrawler as e:
        return jsonify({'code': 4, 'msg': repr(e),
                        'activation_code_status': activation_code_status})


@app.route('/activation_code', methods=['POST'])
def _activation_code(api_call: bool = True):
    global activation_code, activation_code_status, stop_crawler

    if api_call:
        activation_code = request.values.get("code")
        activation_code_status = verify_activation_code(activation_code)
        if not activation_code_status:
            stop_crawler = True

        return jsonify({'code': 0, 'msg': '校验激活码', 'activation_code_status': activation_code_status})
    else:
        while True:
            activation_code_status = verify_activation_code(activation_code)
            if not activation_code_status:
                stop_crawler = True
            time.sleep(60)


def start_active_code_thread():
    """
    子线程定时校验激活码
    :return:
    """
    check_thread = threading.Thread(target=_activation_code, args=(False,))
    check_thread.start()


def check_port_in_use(port, host='127.0.0.1'):
    """检查端口是否被占用，防止重复启动"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host, int(port)))
        s.settimeout(1)
        s.shutdown(2)
        return True
    except:
        return False


if __name__ == '__main__':

    if not check_port_in_use(5001):
        start_active_code_thread()
        pywsgi.WSGIServer(('0.0.0.0', 5001), app).serve_forever()  # 此方式无法抛出此异常：DrissionPage.errors.PageDisconnectedError
        # app.run('0.0.0.0', 5001)
