# coding=utf-8

import time
import json
import re

from flask import request, jsonify

from . import api
from ihome import db, constants
from ihome.utils.response_code import RET


@api.route('/login', methods=['POST'])
def login():
    """
    登录模块
    """
    # 获取登录信息
    print 1111
    login_data = request.get_json()
    if not login_data:
        return jsonify(erron=RET.DATAERR, errmsg=u'参数错误')
    email = login_data.get('email')
    password = login_data.get('password')
    # 校验参数
    if not all([email, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')
    # 校验手机号
    # if not re.match(r'^1[34578]\d{9}$', email):
    #     return jsonify(errno=RET.DATAERR, errmsg='手机号格式错误')
    if email == '123' and password == '123':
        print 123
