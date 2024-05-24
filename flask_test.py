# !/usr/bin/python
# -*- coding: utf-8 -*-
import time

import DrissionPage
import DrissionPage.errors
from DrissionPage import ChromiumPage, ChromiumOptions
from flask import Flask, request, jsonify
from gevent import pywsgi

app = Flask(__name__)

@app.route('/testb', methods=['POST'])
def testb():
    data = request.get_json()
    print(data)
    print(type(data))


@app.route('/testa', methods=['POST'])
def testa():
    try:
        page = ChromiumPage()
        page.get(f'https://news.baidu.com/')

        while True:
            # title = page.ele('xpath://title').text
            # print(title)
            print(page.cookies())
            time.sleep(2)
    except DrissionPage.errors.PageDisconnectedError:
        print('DrissionPage.errors.PageDisconnectedError')

    print(111111111)



if __name__ == '__main__':
    # app.run('0.0.0.0', 5001)
    pywsgi.WSGIServer(('0.0.0.0', 5001), app).serve_forever()
