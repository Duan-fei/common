# -*- coding:utf-8 -*-
__author__ = 'cv'

import json
import logging
import requests
from .utils import recursive_sort
from daisy.utils import datetimeutil, hash

TAOBAO_GW = 'http://gw.api.taobao.com/router/rest'
_conn = requests.session()
timeout = 5

logger = logging.getLogger(__name__)


def send_voice_call(mobile_num, app_key, app_secret, called_show_num, tts_code, tts_param):
    """
    发送语音通知
    :param mobile_num:
    :param app_key:
    :param app_secret:
    :param called_show_num:
    :param voice_code:
    :param tts_code:
    :param tts_param:
    :return:
    """
    send_info = {
        'app_key': app_key,
        'method': "alibaba.aliqin.fc.tts.num.singlecall",
        'called_num': mobile_num,
        'called_show_num': called_show_num,
        'tts_code': tts_code,
        'tts_param': tts_param,
    }
    request_params = gen_params(send_info)
    request_params.append(("sign", make_sign(request_params, app_secret)))

    result = _conn.get(TAOBAO_GW, params=request_params, timeout=timeout)
    logger.debug(result.text)
    data = json.loads(result.text, encoding="utf-8")
    if data.get("error_response", None):
        logging.error("send voice call failed [%s]" % result.text)
        return False

    return True


def send_text_msg_new(mobile_num, app_key, app_secret, template_code, sms_param, sign_name):
    """
    发送短信
    :param mobile_num:
    :param app_key:
    :param app_secret:
    :param template_code:
    :param sms_param:
    :param sign_name:
    :return:
    """
    send_info = {
        'app_key': app_key,
        'method': "alibaba.aliqin.fc.sms.num.send",
        'rec_num': mobile_num,
        'sms_type': 'normal',
        'sms_free_sign_name': sign_name,
        'sms_template_code': template_code,
        'sms_param': sms_param,
    }
    request_params = gen_params(send_info)
    request_params.append(("sign", make_sign(request_params, app_secret)))

    result = _conn.get(TAOBAO_GW, params=request_params, timeout=timeout)
    data = json.loads(result.text, encoding="utf-8")
    if data.get("error_response", None):
        logging.error("send sms failed [%s]" % result.text)
        return False
    return True


def gen_params(params):
    data = {
        'v': "2.0",
        'format': "json",
        'sign_method': "md5",
        'timestamp': datetimeutil.prc_now("%Y-%m-%d %H:%M:%S"),
    }
    for (k, v) in params.items():
        data[k] = v
    return recursive_sort(data)


def make_sign(data, app_secret):
    sign_info = ''
    for param_info in data:
        sign_info = sign_info + param_info[0] + param_info[1]

    sign_info = app_secret + sign_info + app_secret
    return str(hash.md5_hex(unicode(sign_info).encode("utf-8"))).upper()
