# -*- coding: utf-8 -*-
import requests
#
# data = {
#     'username': 'aiyunxia1',
#     'password': '628116',
#     'company_name': 'yuanding1',
#     'email': '15776572136@163.com'
# }
# url = 'http://127.0.0.1:5000/api/v1.0/sign_up'
# response = requests.post(url=url, data=data)
# print response.status_code
# print response.content
data = {
    'uid': '123',
}
url = 'http://127.0.0.1:5000/api/v1.0/get_statement'
response = requests.get(url=url, params=data)
print response.status_code
print response.content
# data = {
#     'username': 'aiyunxia1',
#     'password': '628116'
# }
# url = 'http://127.0.0.1:5000/api/v1.0/login_cre'
# resp = requests.post(url=url, data=data)
# print resp.status_code
# print resp.content


