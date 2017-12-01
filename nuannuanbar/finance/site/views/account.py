# coding:utf-8

import re
import time
import logging

from flask import request, jsonify, current_app

from daisy.views.base import BaseView
from daisy.views.decorators import template_context, templated
from bson import ObjectId
from daisy.globals import db
from flask import session
# 导入状态码信息
from finance.constants import RET
from finance import constants


class LoginView(BaseView):
    """
    登录/登出视图函数
    """
    template_base = 'site/login'
    route_base = 'login'

    @templated()
    def login(self):
        return

    def post_check_login(self):
        # 获取信息
        node_data = request.get_json()
        email = node_data.get('email')
        password = node_data.get('password')

        # 校验用户信息
        if not all([email, password]):
            return jsonify(errno=RET.PARAMERR, errmsg=u'参数缺失')
        try:
            account = db.Account().find_one({'email': str(email)})
        except Exception as e:
            logging.error(e)
            return jsonify(errno=RET.DBERR, errmsg=u'获取用户信息异常')
        if not account:
            return jsonify(errno=RET.USERERR, errmsg=u'用户不存在或被禁用')
        if account and account.get('password') != password:
            return jsonify(errno=RET.PWDERR, errmsg=u'账号或密码错误')
        if account.get('status') == constants.STATE_FAIL:
            return jsonify(errno=RET.USERERR, errmsg=u'您的账户已被禁用')
        session_info = db.Session.find_one({'user_id': account.get('_id')})
        if session_info:
            pass
        else:
            # 缓存用户信息
            spec = {
                'user_id': int(account.get('_id')),
                'name': account.get('name')
            }
            db.Session().apply_form_save(spec)
        logging.info('This user %s' % account.get('_id'))
        data = {
            'user_id': account.get('_id'),
            'name': account.get('name'),
            'status': account.get('status'),
            'role_code': account.get('role_code')
        }
        return jsonify(errno=RET.OK, errmsg='OK', data=data)

    def login_out_port(self):
        """
        退出登录，清除缓存
        :return:
        """
        node_data = request.args
        at_user_id = node_data.get('at_user_id')
        session_info = db.Session.find_one({'user_id': int(at_user_id)})
        if session_info:
            db.Session.remove_by_oid(ObjectId(session_info.get('_id')))
            session.clear()
        return jsonify(errno=RET.OK, errmsg='OK')
