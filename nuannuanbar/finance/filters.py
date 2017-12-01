# -*- coding:utf-8 -*-
__author__ = 'night'
import re
from datetime import datetime, date, timedelta

from jinja2 import evalcontextfilter, escape
from jinja2.utils import Markup

from daisy.utils import json, datetimeutil, convert

from . import app


@app.template_filter()
def prc_format(v, fmt=None):
    return datetimeutil.format_prc(v, fmt)


@app.template_filter()
def prc_date(value):
    return datetimeutil.format_prc(value, "%Y-%m-%d")


@app.template_filter()
def int_date(value):
    value = "%s" % value
    return date(int(value[:4]), int(value[4:6]), int(value[6:8]))


@app.template_filter()
def json_dumps(obj):
    return json.json_dumps(obj)


@app.template_filter()
def strftime(value, fmt='%Y-%m-%d %H:%M:%S %Z'):
    if value is None:
        return ''
    return value.strftime(fmt)


@app.template_filter()
def day2date(value):
    v = str(value)
    return "{0}-{1}-{2}".format(v[:4], v[4:6], v[6:8])


@app.template_filter()
def none_default(value, default):
    if value is None:
        return default
    return value


@app.template_filter()
def minutes(secords):
    v = convert.to_int(secords)
    m = v / 60
    return m


@app.template_filter()
def duration_format(secords):
    v = convert.to_int(secords)
    m = v / 60
    return "%02d:%02d" % (m, v - m * 60)


@app.template_filter()
def duration_minutes(secords):
    v = convert.to_int(secords)
    m = v / 60
    return "%02d" % m


@app.template_filter()
def duration_hour(secords, format="%02dh %02dm %02ds"):
    v = convert.to_int(secords)
    h = v / 3600
    m = (v - h * 3600) / 60
    s = v - h * 3600 - m * 60
    return format % (h, m, s)

@app.template_filter()
def prc_date_int(value):
    return datetimeutil.format_prc(value, "%Y%m%d")

@app.template_filter()
def remain_days(from_time):
    return datetimeutil.remain_days(from_time)
