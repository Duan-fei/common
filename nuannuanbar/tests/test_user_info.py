# coding:utf-8

import requests

import test_config


def test_account():
    # route = '/user/post_add_user/'
    # data = {
    #     'name': '艾艾',
    #     'email': '1eeeeeqweqqq8@163.com',
    #     'city': 1,
    #     'password': '19920116',
    #     'role_code': 1000,
    # }

    # route = '/user/post_compile_user/'
    # data = {
    #     'user_id': 72,
    #     'password': '19921111',
    #
    #
    # }
    # route = '/user/check_password/?user_id=3'
    route = '/user/post_change_status/'
    data = {
        'user_id': 1,
        'status': 100,
        'at_user_id': 3,
    }
    # route = '/user/delete_user/?user_id=71'
    # route = '/user/user_list/?role_code=1000'

    response = requests.post(test_config.url + route, data)
    # response = requests.get(test_config.url + route)
    print response.content.decode('utf-8')


if __name__ == '__main__':
    test_account()