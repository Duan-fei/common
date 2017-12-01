# coding:utf-8

import re
import time
import logging

from datetime import datetime
from flask import request, jsonify, session, g, json

from daisy.views.base import BaseView
from daisy.globals import db

# 导入状态码信息
from finance.constants import RET
from finance import constants


class RegisterView(BaseView):
    """
    账号信息界面
    """
    template_base = 'site/user'
    route_base = 'user'

    def post_add_user(self):
        """添加新用户"""

        # 获取添加信息
        node_data = request.get_json()
        name = node_data.get('name')
        email = node_data.get('email')
        city = node_data.get('city')
        password = node_data.get('password')
        role_code = node_data.get('role_code')
        at_user_id = node_data.get('at_user_id')

        if not at_user_id:
            return jsonify(errno=RET.SESSIONERR, errmsg=u'用户未登录')
        session_info = db.Session.find_one({'user_id': int(at_user_id)})
        if not session_info:
            return jsonify(errno=RET.SESSIONERR, errmsg=u'用户未登录')
        account_info = db.Account.find_one({'_id': int(at_user_id)})
        if account_info.get('role_code') != 1000:
            return jsonify(errno=RET.ROLEERR, errmsg=u'当前为普通用户')
        if account_info.get('status') != 100:
            return jsonify(errno=RET.STATUS, errmsg=u'用户被禁用')

        # 校验参数的完整性
        if not all([name, email, city, password, role_code]):
            return jsonify(errno=RET.PARAMERR, errmsg=u'参数缺失')
        # 校验邮箱
        if not re.match(r'([\w-]+(\.[\w-]+)*@[\w-]+(\.[\w-]+)+)', email):
            return jsonify(errno=RET.DATAERR, errmsg=u'参数错误')
        user_info = db.Account().find_one({'email': email})
        if user_info:
            return jsonify(errno=RET.DATAEXIST, errmsg=u'邮箱已存在')

        account_doc = {
            'name': name,
            'email': email,
            'city': int(city),
            'password': password,
            'role_code': int(role_code),
            'modify': account_info.get('name')
        }
        logging.info('This user %s', account_info.get('_id'))
        # 保存用户信息
        try:
            db.Account().apply_form_save(account_doc)
        except Exception as e:
            logging.error(e)
            return jsonify(errno=RET.DBERR, errmsg=u'存储用户信息异常')
        return jsonify(errno=RET.OK, errmsg=u'添加用户成功')

    def user_list(self):
        """
        获取用户列表信息
        :return:
        """
        node_data = request.args
        # 获取参数
        email = node_data.get('email')
        role_code = node_data.get('role_code')
        status = node_data.get('status')
        page = node_data.get('page', 0)
        at_user_id = node_data.get('at_user_id')
        if not at_user_id:
            return jsonify(errno=RET.SESSIONERR, errmsg=u'用户未登录')
        session_info = db.Session.find_one({'user_id': int(at_user_id)})
        if not session_info:
            return jsonify(errno=RET.SESSIONERR, errmsg=u'用户未登录')
        account_info = db.Account.find_one({'_id': int(at_user_id)})
        # if account_info.get('role_code') != 1000:
        #     return jsonify(errno=RET.ROLEERR, errmsg=u'当前为普通用户')
        if account_info.get('status') != 100:
            return jsonify(errno=RET.STATUS, errmsg=u'用户被禁用')
        resp = db.Account().get_user_list(page=page, email=email, role_code=role_code,
                                          status=status)
        return json.dumps(resp)

    def post_compile_user(self):
        """
        编辑用户信息
        :return:
        """

        node_data = request.get_json()
        # 获取参数
        user_id = node_data.get('user_id', None)
        password = node_data.get('password', None)
        city = node_data.get('city', None)
        role_code = node_data.get('role_code', None)
        at_user_id = node_data.get('at_user_id')

        if not at_user_id:
            return jsonify(errno=RET.SESSIONERR, errmsg=u'用户未登录')
        session_info = db.Session.find_one({'user_id': int(at_user_id)})
        if not session_info:
            return jsonify(errno=RET.SESSIONERR, errmsg=u'用户未登录')
        account_info = db.Account.find_one({'_id': int(at_user_id)})
        if account_info.get('role_code') != 1000:
            return jsonify(errno=RET.ROLEERR, errmsg=u'当前为普通用户')
        if account_info.get('status') != 100:
            return jsonify(errno=RET.STATUS, errmsg=u'用户被禁用')

        user_info = db.Account().find_one({'_id': int(user_id)})
        # 判断用户是否存在
        if not user_info:
            return jsonify(errno=RET.USERERR, errmsg=u'用户不存在')

        data = {}
        # 判断用户是否更改了密码
        if password:
            if user_info.get('password') != password:
                data['password'] = password

        # 判断用户是否更改了城市
        if city:
            if user_info.get('city') != city:
                data['city'] = int(city)

        # 判断用户是否更改了身份
        if role_code:
            if user_info.get('role_code') != role_code:
                data['role_code'] = int(role_code)

        if data == {}:
            return jsonify(errno=RET.OK, errmsg='OK')

        # 更新用户数据
        logging.info('This user %s' % account_info.get('_id'))
        spec = {'_id': user_info.get('_id')}
        try:
            db.Account().update_set(spec, data)
        except Exception as e:
            logging.error(e)
            return jsonify(errno=RET.DBERR, errmsg=u'更新数据异常')
        spec = {
            '_id': user_info.get('_id')
        }
        data = {
            'updated_at': datetime.utcnow,
            'modify': account_info.get('name')
        }
        if account_info.get('updated_at'):
            try:
                db.Account.update_set(spec, data)
            except Exception as e:
                logging.error(e)
                return jsonify(errno=RET.DBERR, errmsg=u'更新用户信息异常')
        return jsonify(errno=RET.OK, errmsg='OK')


    def post_change_status(self):
        """
        更改状态
        :return:
        """
        # 判断当前用户是否为超级管理员
        node_data = request.get_json()
        # 获取信息
        user_id = node_data.get('user_id')
        status = node_data.get('status')
        at_user_id = node_data.get('at_user_id')
        if not at_user_id:
            return jsonify(errno=RET.SESSIONERR, errmsg=u'用户未登录')
        session_info = db.Session.find_one({'user_id': int(at_user_id)})
        if not session_info:
            return jsonify(errno=RET.SESSIONERR, errmsg=u'用户未登录')
        account_info = db.Account.find_one({'_id': int(at_user_id)})
        if account_info.get('role_code') != 1000:
            return jsonify(errno=RET.ROLEERR, errmsg=u'当前为普通用户')
        if account_info.get('status') != 100:
            return jsonify(errno=RET.STATUS, errmsg=u'用户被禁用')

        user_info = db.Account.find_one({'_id': int(user_id)})
        spec = {'_id': user_info.get('_id')}
        # 保存更改信息
        if user_info.get('status') != int(status):
            try:
                db.Account().update_set(spec, {'status': int(status)})
            except Exception as e:
                logging.error(e)
                return jsonify(errno=RET.DBERR, errmsg=u'存储用户信息异常')
        spec = {
            '_id': user_info.get('_id')
        }
        data = {
            'updated_at': datetime.utcnow,
            'modify': account_info.get('name')
        }
        if account_info.get('updated_at'):
            try:
                db.Account.update_set(spec, data)
            except Exception as e:
                logging.error(e)
                return jsonify(errno=RET.DBERR, errmsg=u'更新用户信息异常')
        return jsonify(errno=RET.OK, errmsg='OK')














