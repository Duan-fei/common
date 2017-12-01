# coding:utf-8
from datetime import datetime

import pymongo

mongo = pymongo.MongoClient('127.0.0.1', 27017)
db = mongo.nuanbar


def clear_data():

    db.account.remove({'_id': {'$nin': [1]}})
    db.enter_apply.remove()


if __name__ == '__main__':
    clear_data()