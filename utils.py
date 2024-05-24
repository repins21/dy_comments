import hashlib
import platform
import winreg
import socket

import psutil
import requests


def verify_activation_code(permitKey) -> bool:
    if not permitKey:
        return False

    host_name = socket.gethostname()  # 主机名
    os_name = platform.system()  # 操作系统名称
    os_version = platform.version()  # 操作系统版本
    os_architecture = ''.join(platform.architecture())  # 操作系统架构
    cpu_count = psutil.cpu_count()  # CPU 逻辑核心数
    mem_total = psutil.virtual_memory().total  # 总内存大小
    cpu_model = platform.processor()  # cpu型号

    eq_str = host_name + os_name + os_version + os_architecture + str(cpu_count) + str(mem_total) + cpu_model

    fingerprint = hashlib.md5(eq_str.encode(encoding='utf-8')).hexdigest()

    url = f'http://47.108.130.155:6751/permit/{permitKey}/{fingerprint}'
    response = requests.post(url, timeout=3)
    if response.status_code == 200:
        activation_code_status = True
    else:
        activation_code_status = False

    return activation_code_status


if __name__ == '__main__':
    verify_activation_code('wrtweurodbasdasdsdaa')
