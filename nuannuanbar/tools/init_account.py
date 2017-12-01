# coding:utf-8
from datetime import datetime

import pymongo

mongo = pymongo.MongoClient('127.0.0.1', 27017)
db = mongo.nuanbar


def init_account():
    account_info = {
        '_id': 1,
        'name': '超级管理员',
        'status': 100,
        'city': 1,
        'role_code': 1000,
        'email': 'nnbar@nnbar.com',
        'password': 'nuanbar123',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }

    return db.account.insert(account_info)


if __name__ == '__main__':
    print init_account()
