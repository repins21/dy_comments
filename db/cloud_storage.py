import json

import requests


def save(comments: list):
    headers = {'Content-Type': 'application/json'}

    payload = {
        "permitKey": "",
        "fingerprint": "",
        "comments": comments
    }

    requests.post('http://47.108.130.155:6751/comment/data/save', data=json.dumps(payload), headers=headers)
