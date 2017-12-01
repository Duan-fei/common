# -*- coding:utf-8 -*-
__author__ = 'studyer'
import logging
import requests
from hashlib import md5

logger = logging.getLogger(__name__)
"""SIOO上海希奥科技SMS短信网关接口
"""
_SMS_GW = 'http://210.5.158.31/hy/'

_conn = requests.session()


def send_text_msg(mobile_num, msg, vendor_auth_str):
    """发送下行短信
    :param mobile_num: 手机号,可逗号分隔多个
    :type mobile_num: basestring
    :param msg: 短信内容
    :type msg: basestring
    :param vendor_auth_str: 授权码: 企业代码＋用户密码串联
    :type vendor_auth_str: basestring
    :return:
    :rtype: bool
    """
    auth = md5(vendor_auth_str).hexdigest()
    params = {
        'mobile': mobile_num,
        'auth': auth,
        'msg': msg,
        'expid': 0,
        'uid': 80436,
        'encode': 'utf-8'
    }
    res = _conn.get(_SMS_GW, params=params)
    try:
        result = res.text
        logger.info('mobile: %s, result: %s', mobile_num, result)
    except ValueError:
        return False
    if result[:1] == '0':
        return True
    return False
