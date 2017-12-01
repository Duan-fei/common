# coding:utf-8

import requests

import test_config


def test_account():
    route = '/login/post_check_login/'
    data = {
        'email': 'mm@mm.com',
        'password': '123456',
    }
    # route = '/login/login_out_port/?at_user_id=3'
    response = requests.post(test_config.url + route, data=data)
    print response.content.decode('utf-8')
    print response.cookies.get('god-view_sid')


if __name__ == '__main__':
    test_account()