import re
import time
import json
import requests
#
# for i in range(1):
#     # res = requests.post('http://127.0.0.1:5001/get_comments?search_info=医美')
#     res = requests.post('http://127.0.0.1:5001/get_comments?search_info=https://www.douyin.com/video/7360327123862588723')
#     print(res.text)

params = {
    'sort_type': 1,
    'publish_time': 0,
    'filter_duration': 0,
}

payload = {
    'msg': '私信内容',
    'data': {
        'video_link1': {
            'homepage_link1': [
                'comment11', 'comment22'
            ],
            'homepage_link2': [
                'comment33', 'comment44'
            ]
        },
        'video_link2': {

        }
    }
}
headers = {'Content-Type': 'application/json'}


# res = requests.get('http://127.0.0.1:5001/have_service')
res = requests.post('http://127.0.0.1:5001/activation_code?code=wrtweurodbasdasdsdaa')
res = requests.post('http://127.0.0.1:5001/get_comments?search_info=https://www.douyin.com/video/7366838294635646242', params=params)
print(res.text)


# res = requests.post('http://127.0.0.1:5001/follow_send_msg', data=json.dumps(payload), headers=headers)
# print(res.text)


# for i in range(17):
#     res = requests.post('http://127.0.0.1:5001/get_comments?search_info=医美', params=params)
#     print(res.text)
#     print(len(res.json()['data']['comments_info']))
#     time.sleep(1)
#
# res = requests.get('http://127.0.0.1:5001/stop_crawler')
# print(res.text)




res = requests.post('http://127.0.0.1:5001/testb', data=json.dumps(payload), headers=headers)


# import winreg
#
#
# key_path = r"SOFTWARE\dyComments"
# value_name = "ActivationCode11"
#
# # 创建或打开注册表键
# try:
#     key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
# except FileNotFoundError:
#     key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
#
# old_activation_code = winreg.QueryValueEx(key, value_name)
# print(old_activation_code)
#
# activation_code = "wwwwwww"
# # winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, activation_code)
#
# winreg.CloseKey(key)



# class AppServerSvc(win32serviceutil.ServiceFramework):
#     _svc_name_ = "DYService"
#     _svc_display_name_ = "Dy Comments Service"
#     _svc_description_ = "dy comments"
#
#     def __init__(self, args):
#         win32serviceutil.ServiceFramework.__init__(self, args)
#         self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
#
#     def SvcDoRun(self):
#         self.ReportServiceStatus(win32service.SERVICE_RUNNING)
#         start_active_code_thread()
#         pywsgi.WSGIServer(('0.0.0.0', 5001), app).serve_forever()
#
#     def SvcStop(self):
#         self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
#         win32event.SetEvent(self.hWaitStop)

# if __name__ == '__main__':
    # win32serviceutil.HandleCommandLine(AppServerSvc)
