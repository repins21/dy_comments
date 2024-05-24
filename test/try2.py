
from typing import Callable
import requests
res = requests.get('http://127.0.0.1:5001/stop_crawler')
print(res.text)

#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import socket

# import socket
#
#
# def check_port_in_use(port, host='127.0.0.1'):
#     s = None
#     try:
#         s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         s.settimeout(1)
#         s.connect((host, int(port)))
#         return True
#     except socket.error:
#         return False
#     finally:
#         if s:
#             s.close()
#
#
# if __name__ == '__main__':
#     print(check_port_in_use(5001))


