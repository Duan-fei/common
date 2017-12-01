# coding=utf-8
# 导入正则,实现手机号格式校验
import re
# 导入蓝图
from . import api
# 导入flask内置的方法
from flask import request, jsonify, current_app, session, g
# 导入自定义的状态码
from ihome.utils.response_code import RET
# 导入模型类
from ihome.models import User
# 导入登陆验证码装饰器
from ihome.utils.commons import login_required
# 导入七牛云接口
from ihome.utils.image_storage import storage
# 导入数据库实例
from ihome import db, constants


@api.route('/sessions', methods=['POST'])
def login():
    """
    登陆
    1/获取参数，mobile，password，get_json()
    2/校验参数存在，进一步获取详细参数信息
    3/校验手机号格式，re
    4/查询数据库，验证用户信息存在，
    5/校验查询结果，检查密码正确
    6/缓存用户信息
    7/返回前端，user_id
    :return:
    """
    # 获取参数，mobile,password,args,data,form,method,url,
    user_data = request.get_json()
    # 校验参数存在
    if not user_data:
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
    # 进一步获取详细的参数信息
    mobile = user_data.get('mobile')
    password = user_data.get('password')
    # 校验参数手机号和密码的完整性
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')
    # 校验手机号
    if not re.match(r'^1[34578]\d{9}$', mobile):
        return jsonify(errno=RET.DATAERR, errmsg='手机号格式错误')
    # 查询数据库，确认用户信息的存在，获取到密码信息
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取用户信息异常')
    # 校验查询结果，以及判断密码是否正确
    if user is None or not user.check_password(password):
        return jsonify(errno=RET.DATAERR, errmsg='用户名或密码错误')
    # 缓存用户信息
    session['user_id'] = user.id
    session['name'] = mobile
    session['mobile'] = mobile
    # 返回结果
    return jsonify(errno=RET.OK, errmsg='OK', data={'user_id': user.id})


@api.route('/session', methods=['DELETE'])
@login_required
def logout():
    """
    退出登陆
    1/清除缓存的用户信息
    :return:
    """
    session.clear()
    return jsonify(errno=RET.OK, errmsg='OK')


@api.route('/user', methods=['GET'])
@login_required
def get_user_info():
    """
    获取用户信息
    1/获取用户信息，g.user_id
    2/查询数据库，根据用户id查询用户信息
    3/保存并且校验查询结果
    4/返回结果
    :return:
    """
    # 获取用户id
    user_id = g.user_id
    # 根据用户id查询数据库
    try:
        # User.query.get(user_id)
        user = User.query.filter_by(id=user_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取用户信息异常')
    # 校验查询结果
    if user is None:
        return jsonify(errno=RET.NODATA, errmsg='无效操作')
    # 返回结果，user.to_dict()
    return jsonify(errno=RET.OK, errmsg='OK', data=user.to_dict())


@api.route('/user/avatar', methods=['POST'])
@login_required
def set_user_avatar():
    """
    上传用户头像
    1/获取参数，request.files,参数avatar
    2/校验参数是否存在
    3/调用七牛云接口，avatar.read(),writer()
    4/需要存储图片名称，存储相对路径,即七牛云返回的图片名称
    5/拼接图片绝对路径，七牛云的外链域名和图片名称
    6/返回前端图片信息
    :return:
    """
    # 获取参数,用户id和图片信息
    user_id = g.user_id
    avatar = request.files.get('avatar')
    # 校验参数存在
    if not avatar:
        return jsonify(errno=RET.PARAMERR, errmsg='未上传图片')
    # 读取图片数据，作为参数传给七牛云，实现图片上传
    avatar_data = avatar.read()
    try:
        # 调用七牛云接口，上传图片
        image_name = storage(avatar_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='上传图片失败')
    # 存储图片信息到数据库
    try:
        # 保存图片信息到数据库
        User.query.filter_by(id=user_id).update({'avatar_url': image_name})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        # 写入数据如果发生异常，需要进行回滚操作
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存图片异常')
    # 拼接完整的图片路径
    image_url = constants.QINIU_DOMIN_PREFIX + image_name
    return jsonify(errno=RET.OK, errmsg='OK', data={'avatar_url': image_url})


@api.route('/user/name', methods=['PUT'])
@login_required
def change_user_info():
    """
    修改用户信息
    1/获取参数，通过g变量获取user_id,get_json()
    2/校验参数存在，进一步获取参数信息，name,校验参数存在
    3/查询数据库，更新用户信息，并不需要保留更新结果
    4/更新缓存的用户信息
    5/返回前端name数据
    :return:
    """
    # 获取参数，user_id,以及put请求方法发送的json数据
    req_data = request.get_json()
    # 校验参数
    if not req_data:
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
    # 进一步获取详细的参数信息
    name = req_data.get('name')
    if not name:
        return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')
    # 获取用户id
    user_id = g.user_id
    # 查询数据库，更新用户信息
    try:
        User.query.filter_by(id=user_id).update({'name': name})
        # 提交用户信息
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        # 更新数据发生异常，需要进行回滚操作
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='更新数据失败')
    # 更新缓存的用户名
    session['name'] = name
    # 返回前端
    return jsonify(errno=RET.OK, errmsg='OK', data={'name': name})


@api.route('/user/auth', methods=['POST'])
@login_required
def set_user_auth():
    """
    设置用户实名信息
    1/获取用户id
    2/获取参数，real_name,id_card,用户的身份信息
    3/校验参数存在，进一步获取详细的参数信息，
    4/校验参数的完整性
    5/操作数据库，保存用户信息，update
    6/返回前端
    :return:
    """
    # 获取用户id
    user_id = g.user_id
    # 获取参数，json字符串，用户身份信息
    user_data = request.get_json()
    # 校验参数存在
    if not user_data:
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
    # 进一步获取详细的参数信息
    real_name = user_data.get('real_name')
    id_card = user_data.get('id_card')
    # 校验参数完整性
    if not all([real_name, id_card]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')
    # 保存到数据库
    try:
        # 更新用户实名信息,不建议使用User.query.get(user_id)
        User.query.filter_by(id=user_id, real_name=None, id_card=None).update(
            {'real_name': real_name, 'id_card': id_card})
        # 提交数据
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        # 提交数据如果发生异常，进行回滚
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存用户实名信息异常')
    # 返回结果
    return jsonify(errno=RET.OK, errmsg='OK')


@api.route('/user/auth', methods=['GET'])
@login_required
def get_user_auth():
    """
    获取用户实名信息
    1/获取用户id
    2/根据用户id，查询数据库
    3/校验查询结果
    4/返回前端，user.auth_to_dict();user.to_dict()
    :return:
    """
    # 获取用户id
    user_id = g.user_id
    # 根据用户id查询数据库
    try:
        user = User.query.filter_by(id=user_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取用户实名信息异常')
    # 校验查询结果
    if user is None:
        return jsonify(errno=RET.NODATA, errmsg='无效操作')
    # 返回前端实名信息
    return jsonify(errno=RET.OK, errmsg='OK', data=user.auth_to_dict())


# 检查登陆状态
@api.route('/session', methods=['GET'])
def check_login():
    """
    检查登陆状态：提供用户信息
    1/获取用户的登陆信息
    2/返回前端用户名
    :return:
    """
    # 获取用户的登陆信息,如果用户已登陆，从缓存中获取用户的登陆信息
    name = session.get('name')
    if name is not None:
        return jsonify(errno=RET.OK, errmsg='true', data={'name': name})
    else:
        return jsonify(errno=RET.SESSIONERR, errmsg='false')
