# -*- coding: utf-8 -*-
__author__ = 'zjw'

STATE_INIT = 0
STATE_OK = 100
STATE_FAIL = -100
STATE_ERROR = -50

ADMINISTRATORS = 1000
CONSUMER = 1001


LOCATION = {
    1: u'北京',
    2: u'沈阳',
    3: u'苏州',
    4: u'其他',
}

class RET:
    OK                  = "0"
    DBERR               = "4001"
    NODATA              = "4002"
    DATAEXIST           = "4003"
    DATAERR             = "4004"
    SESSIONERR          = "4101"
    LOGINERR            = "4102"
    PARAMERR            = "4103"
    USERERR             = "4104"
    ROLEERR             = "4105"
    PWDERR              = "4106"
    STATUS              = "4107"
    OVERTIME            = "4108"
    REQERR              = "4201"
    IPERR               = "4202"
    THIRDERR            = "4301"
    IOERR               = "4302"
    SERVERERR           = "4500"
    UNKOWNERR           = "4501"
error_map = {
    RET.OK                    : u"成功",
    RET.DBERR                 : u"数据库查询错误",
    RET.NODATA                : u"无数据",
    RET.DATAEXIST             : u"数据已存在",
    RET.DATAERR               : u"数据错误",
    RET.SESSIONERR            : u"用户未登录",
    RET.LOGINERR              : u"用户登录失败",
    RET.PARAMERR              : u"参数错误",
    RET.USERERR               : u"用户不存在或未激活",
    RET.ROLEERR               : u"用户身份错误",
    RET.STATUS                : u"用户被禁用",
    RET.OVERTIME              : U"用户登录超时",
    RET.PWDERR                : u"密码错误",
    RET.REQERR                : u"非法请求或请求次数受限",
    RET.IPERR                 : u"IP受限",
    RET.THIRDERR              : u"第三方系统错误",
    RET.IOERR                 : u"文件读写错误",
    RET.SERVERERR             : u"内部错误",
    RET.UNKOWNERR             : u"未知错误",
}


