# coding:utf-8

from datetime import datetime

from flask import jsonify, session, g
from daisy.models.base import BaseModel
from daisy.globals import db

from ..utils.date_tool import time_period
from finance.constants import RET
from finance.utils import date_tool


class EnterApply(BaseModel):
    """
    入驻申请模型类
    """
    __collection__ = 'enter_apply'
    use_seq_id = '_id'
    structure = {
        'company_name': basestring,
        'address': basestring,
        'name': basestring,
        'tel': basestring,
        'company_num': basestring,
        'comment': basestring,
        'referrer_tel': basestring,
        'location': int,  # 1北京 2沈阳 3苏州 4其他
        'created_at': datetime,
        'date': basestring,
    }

    default_values = {
        'created_at': datetime.utcnow,
        'date': datetime.utcnow().strftime('%Y-%m-%d')
    }

    def get_enter_list(self, page, location, keyword, start_date, end_date):
        """
        获取入驻信息列表
        :return:
        """

        enter_list = []
        condition = {}
        # 查询条件
        if keyword:
            condition['company_name'] = {'$regex': keyword}
        if location:
            condition['location'] = int(location)
        # 根据时间查询
        if start_date and end_date:
            date_list = time_period(start_date, end_date)
            condition['date'] = {"$in": date_list}

        total_num = db.EnterApply.find(condition).count()
        page_num, remainder = divmod(total_num, 10)

        if remainder == 0:
            page_num = page_num
        else:
            page_num = page_num + 1

        if page == 0:
            page = page + 1
        for enter_info in db.EnterApply.find(condition).sort('_id', -1).limit(10).skip((int(page)-1) * 10):
            # 保存查询到的数据
            enter_list.append({
                '_id': enter_info.get('_id'),
                'location': enter_info.get('location'),
                'created_at': date_tool.utc_prc(enter_info.get('created_at')).strftime('%Y-%m-%d %H:%M:%S'),
                'company_name': enter_info.get('company_name'),
                'address': enter_info.get('address'),
                'company_num': enter_info.get('company_num'),
                'name': enter_info.get('name'),
                'tel': enter_info.get('tel'),
                'comment': enter_info.get('comment'),
                'referrer_tel': enter_info.get('referrer_tel'),
            })

        ret = {'errno': RET.OK, 'errmsg': 'OK',
               'data': {'current_page': page, 'total': total_num, 'total_page': page_num, 'enter': enter_list}}
        return ret








