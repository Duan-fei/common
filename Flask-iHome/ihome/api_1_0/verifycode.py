# coding=utf-8

# 导入随机数模块，生成短信验证码
import random
# 导入正则模块，实现校验手机号格式
import re
# 导入蓝图
from . import api
# 导入captcha，生成图片验证码
from ihome.utils.captcha.captcha import captcha
# 导入redis实例,导入常量信息，
from ihome import redis_store, constants, db
# 导入flask内置的模块current_app
from flask import current_app, jsonify, make_response, request, session
# 导入自定义状态码
from ihome.utils.response_code import RET
# 导入云通信扩展，实现发送短信
from ihome.utils import sms
# 导入模型类型
from ihome.models import User


@api.route('/imagecode/<image_code_id>', methods=['GET'])
def generate_image_code(image_code_id):
    """
    生成图片验证码
    1/调用第三方扩展captcha，实现图片验证码的生成
    2/把图片验证码缓存到redis中
    3/返回图片验证码
    :param image_code_id:
    :return:
    """
    # 调用captcha实现图片验证码的生成
    name, text, image = captcha.generate_captcha()
    # 把图片验证码缓存到redis中
    try:
        redis_store.setex('ImageCode_' + image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存图片验证码异常')
    else:
        # 调用flask内置的make_response，用来返回图片，以及设置响应头
        # return 'hello world'
        response = make_response(image)
        response.headers['Content-Type'] = 'image/jpg'
        return response


@api.route('/smscode/<mobile>', methods=['GET'])
def send_sms_code(mobile):
    """
    发送短信验证码:获取参数/校验参数/查询数据/返回结果
    1/获取参数，mobile/image_code/image_code_id，request.args.get('text')
    2/校验参数完整性
    3/校验手机号，re正则模块
    4/校验图片验证码，先从redis中获取真实的图片验证码
    5/比较图片验证码是否一致
    6/构造随机数，准备发送短信
    7/调用云通信实现发送短信
    8/验证发送是否成功
    9/返回前端响应结果
    :param mobile:
    :return:
    """
    # 获取参数,图片验证码和图片验证码编号
    image_code = request.args.get('text')
    image_code_id = request.args.get('id')
    # 校验参数完整性
    # if mobile and image_code and image_code_id:
    # any和all方法一般用来校验参数存在或完整性
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
    # 进一步校验参数，手机号
    if not re.match(r'^1[34578]\d{9}$', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号格式错误')
    # 尝试获取真实的图片验证码
    try:
        real_image_code = redis_store.get('ImageCode_' + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取图片验证码异常')
    # 校验查询结果
    if not real_image_code:
        return jsonify(errno=RET.DATAERR, errmsg='图片验证码过期')
    # 比较图片验证码,忽略大小写
    if real_image_code.lower() != image_code.lower():
        return jsonify(errno=RET.DATAERR, errmsg='图片验证码错误')
    # 删除缓存中的图片验证码
    try:
        redis_store.delete('ImageCode_' + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
    # 验证手机号是否已注册
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询数据库异常')
    else:
        # 校验查询结果
        if user:
            return jsonify(errno=RET.DATAEXIST, errmsg='手机号已注册')
    # 构造随机数，准备发送短信
    sms_code = '%06d' % random.randint(1, 999999)
    # 首先把短信验证码存储缓存中
    try:
        redis_store.setex('SMSCode_' + mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存短信验证码异常')
    # 调用云通信接口，发送短信
    try:
        ccp = sms.CCP()
        # 调用云通信的模板方法发送短信，需要mobile/短信内容/过期时间为分钟/模板编号
        result = ccp.send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES / 60], 1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='发送短信异常')
    # 校验发送结果
    # if result = 0:
    if 0 == result:
        return jsonify(errno=RET.OK, errmsg='OK')
    else:
        return jsonify(errno=RET.THIRDERR, errmsg='发送短信失败')


@api.route('/users', methods=['POST'])
def register():
    """
    注册用户
    1/获取参数，mobile/sms_code/password
    2/校验参数完整性
    3/校验手机号
    4/校验短信验证码，尝试从redis中获取真实的短信验证码
    5/校验查询结果，用来比对短信验证码内容
    6/判断用户是否已经注册
    7/存储用户注册信息，User(name=name,mobile=mobile),提交数据
    8/缓存用户信息，session来存储用户信息
    9/返回响应数据
    :return:
    """
    # 获取参数，mobile,sms_code,password,使用get_json()获取前端发送的json数据
    user_data = request.get_json()
    # 校验参数是否存在
    if not user_data:
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
    # 进一步获取参数信息
    # user_data['mobile']
    mobile = user_data.get('mobile')
    sms_code = user_data.get('sms_code')
    password = user_data.get('password')
    # 校验参数完整性
    if not all([mobile, sms_code, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')
    # 校验手机号
    if not re.match(r'^1[34578]\d{9}$', mobile):
        return jsonify(errno=RET.DATAERR, errmsg='手机号格式错误')
    # 校验短信验证码,尝试从redis中获取数据
    try:
        real_sms_code = redis_store.get('SMSCode_' + mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取短信验证码异常')
    # 校验查询结果
    if not real_sms_code:
        return jsonify(errno=RET.DATAEXIST, errmsg='短信验证码过期')
    # 比较短信验证码
    if real_sms_code != str(sms_code):
        return jsonify(errno=RET.DATAERR, errmsg='短信验证码错误')
    # 比较过后，首先删除redis缓存中的真实短信验证码
    try:
        redis_store.delete('SMSCode_' + mobile)
    except Exception as e:
        current_app.logger.error(e)
    # 校验手机号是否已注册
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询数据异常')
    else:
        # 校验手机号是否已注册
        if user:
            return jsonify(errno=RET.DATAEXIST, errmsg='手机号已注册')
    # 存储用户信息，使用模型类存储用户注册信息
    user = User(name=mobile, mobile=mobile)
    # 通过user.password调用了generate_password_hash方法，实现密码的加密存储
    user.password = password
    try:
        # 调用数据库会话对象，用来保存用户注册信息，提交数据到mysql数据库中
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        # 如果存储数据发生异常，需要进行回滚操作
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存用户信息异常')
    # 缓存用户信息
    session['user_id'] = user.id
    session['name'] = mobile
    session['mobile'] = mobile
    # 返回前端响应数据
    return jsonify(errno=RET.OK, errmsg='OK', data=user.to_dict())




