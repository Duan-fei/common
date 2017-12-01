#!/usr/bin/env python
# coding:utf-8

import re
import json
import logging

from flask import request, jsonify, make_response

from daisy.views.base import BaseView
from daisy.views.decorators import template_context
from daisy.globals import db

# 导入状态码信息
from finance.constants import RET, LOCATION


class EnterApply(BaseView):
    """
    入驻申请
    """
    template_base = 'site'
    route_base = ''

    def post_enter_apply(self):
        node_data = request.get_json()
        # 进一步获取详细参数
        company_name = node_data.get('company_name')
        address = node_data.get('address')
        name = node_data.get('name')
        tel = node_data.get('tel')
        company_num = node_data.get('company_num', None)
        comment = node_data.get('comment', None)
        referrer_tel = node_data.get('referrer_tel', None)
        location = node_data.get('location')
        # 校验参数信息的完整性
        if not all([company_name, address, name, tel]):
            return jsonify(errno=RET.PARAMERR, errmsg=u'参数缺失')
        # 校验手机号
        if not re.match(r'^1[34578]\d{9}$', tel):
            return jsonify(errno=RET.DATAERR, errmsg=u'手机号格式错误')
        data = {
            'company_name': company_name,
            'address': address,
            'name': name,
            'tel': tel,
            'company_num': str(company_num),
            'comment': comment,
            'referrer_tel': referrer_tel,
            'location': location
        }
        try:
            # 保存入驻信息
            db.EnterApply().apply_form_save(data)
            return jsonify(errno=RET.OK, errmsg='OK')
        except Exception as e:
            logging.error(e)
            return jsonify(errno=RET.DBERR, errmsg='保存用户信息异常')

    def enter_list(self):
        """
        获取入驻列表信息
        :return:
        """
        node_data = request.args
        # 获取参数信息
        page = node_data.get('page', 0)
        keyword = node_data.get('keyword')
        location = node_data.get('location')
        start_date = node_data.get('start_date')
        end_date = node_data.get('end_date')
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
        resp = db.EnterApply().get_enter_list(page=page, location=location, keyword=keyword,
                                              start_date=start_date, end_date=end_date)
        return json.dumps(resp)



