# -*- coding: utf-8 -*-
# 导入蓝图
from . import api
# 导入flask内置的方法
from flask import request, jsonify, current_app
# 导入模型类
from ihome.models import Account
from ihome.utils.response_code import RET
from ihome import db


@api.route('/sign_up', methods=['POST'])
def register():
    """
    注册
    :return:
    """
    sign_data = request.get_json()
    if not sign_data:
        return jsonify(errno=RET.DATAERR, errmsg=u'数据错误')
    username = sign_data.get('username')
    company_name = sign_data.get('company_name')
    password = sign_data.get('password')
    email = sign_data.get('email')

    if not all([username, password, company_name, email]):
        return jsonify(errno=RET.DATAERR, errmsg=u'数据错误')

    # 查数据库
    try:
        user_info = Account.query.filter_by(username=username).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.NODATA, errmsg=u'没有用户信息')
    if user_info:
        return jsonify(errno=RET.DATAEXIST, errmsg=u'数据已存在')

    user = Account(username=username, company_name=company_name, email=email)
    user.password = password
    try:
        # 调用数据库会话对象，用来保存用户注册信息，提交数据到mysql数据库中
        db.session.add(user)
        db.session.commit()
        return jsonify(errno=RET.OK, errmsg=u'ok')
    except Exception as e:
        current_app.logger.error(e)
        # 如果存储数据发生异常，需要进行回滚操作
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存用户信息异常')


