# -*- coding:utf-8 -*-
__author__ = 'zjw'

import functools

from functools import wraps

from flask import redirect, session, render_template, abort, request
from daisy.globals import current_visitor
from daisy.globals import db
from finance import config
from finance.utils import sign


def _goto_auth_page():
    return redirect('/login/')


def _goto_home_page():
    return redirect('/')


def _user_disable():
    session.clear()
    return render_template('site/login.html', flag='用户已禁用')


def require_login(f):
    @functools.wraps(f)
    def _f(*args, **kwargs):
        token = session.get('{0}_account_code'.format(config.MEMCACHED_FLAG))
        if not token:
            return _goto_auth_page()
        return f(*args, **kwargs)

    return _f


def api_auth(f):
    @functools.wraps(f)
    def _f(*args, **kwargs):
        rn_data = request.args

        if not sign.auth_sign(config.MSG_SECRET, rn_data):
            return abort(403)

        return f(*args, **kwargs)

    return _f


def permission_required(permissions):  # 用于检查常规权限
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            role_id = session.get('role_id')
            permission_list = db.Role().get_permissions(role_id)
            do_redirect = True
            if not permission_list:
                session.clear()
                return _goto_auth_page()
            for permission in permissions:
                if permission in permission_list:
                    do_redirect = False
            if do_redirect:
                return _goto_home_page()
            return f(*args, **kwargs)

        return decorated_function

    return decorator
