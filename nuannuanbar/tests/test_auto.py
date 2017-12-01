# coding:utf-8

import requests

import test_config


def test_account():
    route = '/user/add_add_account/'

    response = requests.get(test_config.url + route)
    print response.content.decode('utf-8')


if __name__ == '__main__':
    test_account()