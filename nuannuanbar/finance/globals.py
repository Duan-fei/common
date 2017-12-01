# -*- coding:utf-8 -*-
"""
All global objects
"""
from werkzeug.local import LocalProxy
from flask import current_app, _request_ctx_stack
from finance import config


# AoAo = AoAoClient(config.AOAO_URL, ser_key=config.AOAO_SER_KEY, acc_key=config.AOAO_ACC_KEY)


def _get_current_db():
    return current_app.mongo.get_db()


def _lookup_visitor_object():
    top = _request_ctx_stack.top
    if top is None:
        raise RuntimeError('working outside of request context')
    return getattr(top, 'visitor')


db = LocalProxy(_get_current_db)
current_visitor = LocalProxy(_lookup_visitor_object)
