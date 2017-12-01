# -*- coding:utf-8 -*-
import calendar


def create_week(year, month):
    day = calendar.monthrange(year, month)[1]
    return {
        1: u'第一周 1-10',
        2: u'第二周 11-20',
        3: u'第三周 21-%s' % day,
    }


def create_preview_week(year, month):
    day = calendar.monthrange(year, month)[1]
    return {
        1: u'第一周 1-10',
        2: u'第二周 1-20',
        3: u'第三周 1-%s' % day,
    }
