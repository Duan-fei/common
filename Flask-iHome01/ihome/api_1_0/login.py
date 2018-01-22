# -*- coding: utf-8 -*-
# 导入蓝图
from . import api
# 导入flask内置的方法
from flask import request, jsonify, current_app, g
# 导入模型类
from ihome.models import Account
from ihome.utils.response_code import RET
import pymysql, json


@api.route('/login_cre', methods=['POST'])
def login():
    """
    登
    1/获取参，password，get_json()
    :return:
    """
    # 获取参数，usename, password, args, method, url,
    user_data = request.get_json()
    # 校验参数存在
    if not user_data:
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
    # 进一步获取详细的参数信息
    username = user_data.get("username")
    password = user_data.get("password")
    if not all([username, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数缺失")
    try:
        user_info = Account.query.filter_by(username=username).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取用户信息异常')

    # 判断数据库中是否存在此用户
    if not user_info:
        return jsonify(errno=RET.USERERR, errmsg=u'用户不存在或未激活')

    # 校验查询结果，以及判断密码是否正确
    if not user_info.check_password(password):
        return jsonify(errno=RET.DATAERR, errmsg='用户名或密码错误')

    return jsonify(errno=RET.OK, errmsg="OK", data=user_info.to_dict())


@api.route('/get_statement', methods=['GET'])
def get_statement():
    """
    返回报表列表
    :return:
    """
    uid = request.args.get('uid')
    print uid
    # uid = request.args.get('uid')
    # todo 中间查询数据
    user = 'spider'
    # host = 'rds93vu04hr3rn0o2d5io.mysql.rds.aliyuncs.com'
    host = 'rds93vu04hr3rn0o2d5io.mysql.rds.aliyuncs.com'
    db = 'spider'
    port = 3306
    passwd ='abcde123!@#'

    conn = pymysql.connect(user=user, host=host, db=db, port=port, passwd=passwd)
    cur = conn.cursor()
    data = {}
    for i in range(1, 73):
        sqlnum = '%03d' % i
        name = 'credit_%s' % sqlnum
        credit = {}
        cur.execute('''select * from credit_%s where uid="%s"''' % (sqlnum, uid))
        info = cur.fetchall()
        if info:
            for i in info:
                if i[1] is None:
                    print(1111)
                else:
                    credit[i[2]] = i[1]
                    data[name] = credit
        else:
            data[name] = None

    json_data = json.dumps(data)

    return jsonify(errno=RET.OK, errmsg=u'OK', data=json_data)
