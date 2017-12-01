# coding:utf-8

from datetime import datetime

from flask import jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from daisy.models.base import BaseModel
from daisy.globals import db

from finance import constants
from finance.constants import RET
from finance.utils import date_tool


class Account(BaseModel):
    """
    账号模型类
    """
    __collection__ = 'account'
    use_seq_id = '_id'
    structure = {
        'city': int,
        'name': basestring,
        'email': basestring,
        'password': basestring,
        'role_code': int,
        'status': int,
        'modify': basestring,
        'created_at': datetime,
        'updated_at': datetime,
    }
    default_values = {
        'created_at': datetime.utcnow,
        'updated_at': datetime.utcnow,
        'status': constants.STATE_OK,
    }

    # 获取用户信息列表
    def get_user_list(self, page, role_code, email, status):
        account_list = []
        condition = {}
        # 查询条件
        if email:
            email = email.replace(" ", "")
            condition['email'] = {'$regex': email}
        if status:
            condition['status'] = int(status)
        if role_code:
            condition['role_code'] = int(role_code)

        total_num = db.Account().find(condition).count()
        page_num, remainder = divmod(total_num, 10)

        if remainder == 0:
            page_num = page_num
        else:
            page_num = page_num + 1

        if page == 0:
            page = page + 1

        # 遍历出所有数据
        for account_info in db.Account.find(condition).sort('_id', -1).limit(10).skip(10 * (int(page)-1)):
            # 保存查询到的数据
            account_list.append({
                'id': account_info.get('_id'),
                'city': account_info.get('city'),
                'name': account_info.get('name'),
                'email': account_info.get('email'),
                'password': account_info.get('password'),
                'created_at': date_tool.utc_prc(account_info.get('created_at')).strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': date_tool.utc_prc(account_info.get('updated_at')).strftime('%Y-%m-%d %H:%M:%S'),
                'status': account_info.get('status'),
                'role_code': account_info.get('role_code'),
                'modify': account_info.get('modify')
            })

        ret = {'errno': RET.OK, 'errmsg': 'OK',
               'data': {'current_page': page, 'total': total_num, 'total_page': page_num, 'account': account_list}}
        return ret














