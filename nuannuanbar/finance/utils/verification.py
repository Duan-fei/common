# coding:utf-8

import functools
import time

from flask import g, session, jsonify
from finance.constants import RET
from daisy.globals import db


def login_required(f):
    """要求用户权限登录的验证装饰器"""
    # functools让被装饰的函数名称不会被改变
    @functools.wraps(f)
    def wrapper(user_id, *args, **kwargs):
        # 从session数据中获取user_id
        session_info = db.Session.find_one({'user_id': user_id})
        if not session_info:
            # 如果session中不存在user_id，表示用户未登录
            return jsonify(errno=RET.SESSIONERR, errmsg=u"用户未登录")
        # expire_time = session_info.get('expire')

        account = db.Account.find_one({'_id': int(user_id)})
        if account.get('status') != 100:
            return jsonify(errno=RET.SESSIONERR, errmsg=u'用户被禁用')
        if account.get('role_code') != 1000:
            return jsonify(errno=RET.ROLEERR, errmsg=u'当前为普通用户')
        else:
            # 表示用户已登录，将可能用到的user_id用户编号保存到g中，供视图函数使用
            g.user_id = user_id
            return f(*args, **kwargs)
    return wrapper


def verification(at_user_id):
    """用户权限登录验证"""
    session_info = db.Session.find_one({'user_id': int(at_user_id)})
    print session_info, 'AAAA'
    if not session_info:
        return jsonify(errno=RET.SESSIONERR, errmsg=u'用户未登录')
    expires = session_info.get('expires')
    now_time = int('%.0f' % time.time())
    if now_time < expires:
        return jsonify(errno=RET.SESSIONERR, errmsg=u'账号已超时请重新登陆')


def verification_st_rol(at_user_id):
    account_info = db.Account.find_one({'_id': int(at_user_id)})
    print account_info
    if account_info.get('role_code') != 1000:
        return jsonify(errno=RET.ROLEERR, errmsg=u'当前为普通用户')
    if account_info.get('status') != 100:
        return jsonify(errno=RET.ROLEERR, errmsg=u'用户被禁用')


