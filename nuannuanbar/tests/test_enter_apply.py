# coding:utf-8

import requests
import test_config


def test_enter_apply():
    route = '/post_enter_apply/'

    data = {
        'company_name': u'hahahahah',
        'address': u'北京市asdasdasd',
        'name': u'测试',
        'tel': '15776572158',
        'company_num': 10,
        'comment': '哈哈哈',
        'referrer_tel': '15500055605',
        # 'location': 2,
    }
    response = requests.post(test_config.url + route, data=data)

    # route = "/enter_list/?start_date=2017-11-13&end_date=2017-11-16"

    # response = requests.get(test_config.url + route)
    print response.content.decode('utf-8')


if __name__ == '__main__':
    test_enter_apply()
