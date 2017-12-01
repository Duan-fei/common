# coding=utf-8
# 导入datetime,日期格式化操作
import datetime
# 导入json模块
import json
# 导入蓝图
from . import api
# 导入数据库实例
from ihome import redis_store, constants, db
# 导入应用上下文
from flask import current_app, jsonify, session, g, request
# 导入城区模型类
from ihome.models import Area, House, Facility, HouseImage, User, Order
# 导入自定义状态码
from ihome.utils.response_code import RET
# 导入登陆验证装饰器
from ihome.utils.commons import login_required
# 导入七牛云
from ihome.utils.image_storage import storage


@api.route('/areas', methods=['GET'])
def get_area_info():
    """
    获取城区信息
    1/尝试从ｒｅｄｉｓ中获取缓存的区域,
    2/校验获取结果,jsonify(errno=RET.OK,errmsg='OK')
    3/查询ｍｙｓｑｌ数据库,校验查询结果，如未获取到，终止视图函数
    4/把城区信息添加到缓存中,需要转换成json格式
    5/返回城区信息
    :return:
    """
    # 尝试从缓存中获取区域信息
    try:
        areas = redis_store.get('area_info')
    except Exception as e:
        current_app.logger.error(e)
        areas = None
    # 校验查询结果
    if areas:
        # 记录访问redis数据城区信息的时间
        current_app.logger.info('hit area info redis')
        # 因为ｒｅｄｉｓ中存储的数据是ｊｓｏｎ字符串，所以直接拼接字符串返回，不用调用jsonify方法
        return '{"errno":0,"errmsg":"OK","data":%s}' % areas
    # 查询ｍｙｓｑｌ数据库
    try:
        areas = Area.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取城区信息异常')
    # 校验查询结果
    if not areas:
        return jsonify(errno=RET.NODATA, errmsg='查询无数据')
    # 定义列表存储区域信息
    areas_list = []
    for area in areas:
        # 调用模型类的to_dict()方法，获取城区信息
        areas_list.append(area.to_dict())
    # 把城区信息转成ｊｓｏｎ格式，存入缓存中
    areas_json = json.dumps(areas_list)
    # 把ｊｓｏｎ数据存入缓存中
    try:
        redis_store.setex('area_info', constants.AREA_INFO_REDIS_EXPIRES, areas_json)
    except Exception as e:
        current_app.logger.error(e)
    # 直接返回城区信息
    return '{"errno":0,"errmsg":"OK","data":%s}' % areas_json


@api.route('/houses', methods=['POST'])
@login_required
def save_house_info():
    """
    保存房屋信息
    1/获取参数，获取用户ｉｄ，get_json()方法获取参数
    2/校验参数存在
    3/进一步获取详细的参数信息
    4/校验参数的完整性
    5/统一前后端的价格信息，float/int
    6/准备存入房屋基本信息
    7/判断设施信息是否有数据，如果有数据，过滤设施编号信息
    8/把房屋信息存入数据库
    9/返回结果,house_id
    :return:
    """
    # 获取用户ｉｄ
    user_id = g.user_id
    # 获取房屋基本信息
    house_data = request.get_json()
    # 校验参数存在
    if not house_data:
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
    # 进一步获取详细的房屋基本信息
    title = house_data.get('title')
    price = house_data.get('price')
    area_id = house_data.get('area_id')
    address = house_data.get('address')
    room_count = house_data.get('room_count')
    acreage = house_data.get('acreage')
    unit = house_data.get('unit')
    capacity = house_data.get('capacity')
    beds = house_data.get('beds')
    deposit = house_data.get('deposit')
    min_days = house_data.get('min_days')
    max_days = house_data.get('max_days')
    # 校验参数完整性
    if not all(
            [title, price, area_id, address, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')
    # 处理价格信息
    try:
        # 由于前端的价格信息是以元为单位，数据库中存储的是以分为单位，所以需要单位转换
        price = int(float(price) * 100)
        deposit = int(float(deposit) * 100)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg='价格转换异常')
    # 构造模型类对象，准备存储房屋基本信息
    house = House()
    house.user_id = user_id
    house.area_id = area_id
    house.title = title
    house.price = price
    house.address = address
    house.room_count = room_count
    house.acreage = acreage
    house.unit = unit
    house.capacity = capacity
    house.beds = beds
    house.deposit = deposit
    house.min_days = min_days
    house.max_days = max_days
    # 尝试获取房屋配套设施信息
    facility = house_data.get('facility')
    # 校验参数存在
    if facility:
        try:
            # 过滤设施编号是和数据库中房屋设施表的编号是对应的
            facilities = Facility.query.filter(Facility.id.in_(facility)).all()
            house.facilities = facilities
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='获取设施信息异常')
    try:
        # 保存数据
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        # 写入数据发生异常，进行回滚
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存房屋信息异常')
    # 返回数据
    return jsonify(errno=RET.OK, errmsg='OK', data={'house_id': house.id})


@api.route('/houses/<int:house_id>/images', methods=['POST'])
@login_required
def save_house_image(house_id):
    """
    保存房屋图片
    1/获取参数，house_image
    2/校验参数存在
    3/校验房屋是否存在,读取图片数据，调用七牛云接口上传图片
    4/构造模型类对象，保存房屋图片数据
    5/判断房屋主图片是否设置，如未设置保存当前图片为房屋主图片
    6/保存数据到数据库中
    7/拼接完整的图片url返回前端
    :param house_id:
    :return:
    """
    # 获取参数
    image = request.files.get('house_image')
    # 校验参数
    if not image:
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
    # 查询数据库，确定房屋存在
    try:
        # House.query.filter_by(id=house_id).first()
        # House.queyr.filter(House.id=house_id).first()
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询房屋信息异常')
    # 校验查询结果
    if not house:
        return jsonify(errno=RET.NODATA, errmsg='房屋不存在')
    # 读取图片数据
    image_data = image.read()
    # 调用七牛云接口
    try:
        image_name = storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='上传图片异常')
    # 构造模型类对象，准备存储图片信息
    house_image = HouseImage()
    house_image.house_id = house_id
    house_image.url = image_name
    # 提交房屋图片表的模型类对象
    db.session.add(house_image)
    # 判断房屋主图片是否设置
    if not house.index_image_url:
        house.index_image_url = image_name
        # 提交房屋表的模型类对象
        db.session.add(house)
    # 保存数据到数据库中
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        # 如果存储数据发生异常，进行回滚
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存数据异常')
    # 拼接图片完整url，返回前端
    image_url = constants.QINIU_DOMIN_PREFIX + image_name
    return jsonify(errno=RET.OK, errmsg='OK', data={'url': image_url})


@api.route('/houses/index', methods=['GET'])
def get_house_index():
    """
    项目首页幻灯片信息展示
    1/尝试从redis中获取房屋信息
    2/校验获取结果
    3/查询mysql数据库,默认把成交量最高的五套房屋数据返回
    4/校验查询结果
    5/定义列表存储多条数据,判断房屋是否设置主图片信息,如未设置,默认不添加数据
    6/把数据存入缓存中
    7/返回前端最终的查询结果
    :return:
    """
    # 查询redis缓存中的房屋信息
    try:
        ret = redis_store.get('home_page_data')
    except Exception as e:
        current_app.logger.error(e)
        ret = None
    # 校验查询结果
    if ret:
        # 记录访问缓存数据的时间,由于redis中存储的数据是json格式,所以直接拼接字符串返回
        current_app.logger.info('hit house index info redis')
        return '{"errno":0,"errmsg":"OK","data":%s}' % ret
    # 查询mysql数据库
    try:
        # 安装房屋成就次数倒叙查询,获取成交量最高的五套房屋
        houses = House.query.order_by(House.order_count.desc()).limit(constants.HOME_PAGE_MAX_HOUSES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询房屋信息异常')
    # 校验查询结果
    if not houses:
        return jsonify(errno=RET.NODATA, errmsg='无房屋数据')
    # 存储查询结果,遍历房屋数据,调用模型类的to_basic_dict()方法
    houses_list = []
    for house in houses:
        # 判断房屋主图片是否设置
        if not house.index_image_url:
            continue
        houses_list.append(house.to_basic_dict())
    # 序列化数据
    json_houses = json.dumps(houses_list)
    # 先把数据存入缓存中
    try:
        redis_store.setex('home_page_data', constants.HOME_PAGE_DATA_REDIS_EXPIRES, json_houses)
    except Exception as e:
        current_app.logger.error(e)
    # 拼接字符串,返回响应数据
    resp = '{"errno":0,"errmsg":"OK","data":%s}' % json_houses
    return resp


@api.route('/houses/<int:house_id>', methods=['GET'])
def get_house_detail(house_id):
    """
    获取房屋详情信息
    1/获取用户信息,用来校验用户身份
    2/获取house_id,校验参数
    3/尝试从缓存中查询房屋详情信息
    4/校验查询结果
    5/如未获取数据,查询mysql数据库
    6/转换数据格式,调用模型类中的to_full_dict()方法
    7/序列化数据,把数据存入缓存中
    8/返回结果
    :param house_id:
    :return:
    """
    # 获取参数,-1用来判断访问当前页面的用户,是否是房东,如果是房东,隐藏下单接口,如是普通用户,提供下单接口
    user_id = session.get('user_id', '-1')
    # 校验房屋参数是否存在
    if not house_id:
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
    # 尝试从redis中获取房屋详情信息
    try:
        ret = redis_store.get('house_info_%s' % house_id)
    except Exception as e:
        current_app.logger.error(e)
        ret = None
    # 校验查询结果,如果获取到数据直接拼接字符串返回
    if ret:
        current_app.logger.info('hit house detail info redis')
        return '{"errno":0,"errmsg":"OK","data":{"user_id":%s,"house":%s}}' % (user_id, ret)
    # 查询mysql数据库,根据房屋id进行精确查询
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询房屋详情信息异常')
    # 校验查询结果
    if not house:
        return jsonify(errno=RET.NODATA, errmsg='无房屋数据')
    # 获取房屋详情信息,转换格式,调用模型类中的to_full_dict()方法
    try:
        house_data = house.to_full_dict()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg='房屋数据格式错误')
    # 序列化数据,转成json格式,存入缓存中
    json_house = json.dumps(house_data)
    try:
        redis_store.setex('house_info_%s' % house_id, constants.HOUSE_DETAIL_REDIS_EXPIRE_SECOND, json_house)
    except Exception as e:
        current_app.logger.error(e)
    # 构造响应数据返回结果
    resp = '{"errno":0,"errmsg":"OK","data":{"user_id":%s,"house":%s}}' % (user_id, json_house)
    return resp


@api.route('/houses', methods=['GET'])
def get_houses_list():
    """
    获取房屋列表信息
    1/尝试获取参数,area_id/start_date_str/end_date_str/sort_key/page
    2/对日期进行格式化处理
    3/对页数进行格式化处理
    4/查询redis缓存数据库,校验查询结果,需要使用哈希类型,便于统一设置数据的过期时间
    5/查询mysql数据库,定义过滤条件,使用列表存储,filter_params = [area_id] House.query.filter(*filter_params)
    6/根据排序条件进行排序查询,booking/price/create_time
    7/使用paginate进行分页房屋数据
    8/对分页后的数据进行遍历存储,获取房屋基本信息
    9/把数据放入缓存中
    10/判断用户访问的页数小于等于分页后的总页数
    11/对多条数据统一存储,需要使用事务操作,pipeline()
    12/返回结果
    :return:
    """
    # 尝试获取参数信息
    area_id = request.args.get('aid', '')
    start_date_str = request.args.get('sd', '')
    end_date_str = request.args.get('ed', '')
    sort_key = request.args.get('sk', 'new')
    page = request.args.get('p', '1')
    # 对日期进行格式化
    try:
        start_date, end_date = None, None
        if start_date_str:
            start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
        if end_date_str:
            end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")
        # 断言用户选择的开始日期小于等于结束日期
        if start_date_str and end_date_str:
            assert start_date <= end_date
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg='日期格式错误')
    # 对页数进行格式化
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg='页数格式化错误')
    # 尝试从redis中获取房屋列表信息
    try:
        # 缓存中使用哈希数据类型存储数据
        redis_key = "houses_%s_%s_%s_%s" % (area_id, start_date_str, end_date_str, sort_key)
        ret = redis_store.hget(redis_key, page)
    except Exception as e:
        current_app.logger.error(e)
        ret = None
    # 校验查询结果
    if ret:
        # 记录访问缓存数据的时间
        current_app.logger.info('hit houses list info redis')
        return ret
    # 查询mysql数据库
    try:
        # 定义过滤条件
        filter_params = []
        # 判断区域信息
        #
        if area_id:
        # if area_id or House.area_id == area_id:
            filter_params.append(House.area_id == area_id)
        # 判断日期信息,如果用户选择了开始日期和结束日期
        if start_date and end_date:
            # 查询所有有冲突的订单信息
            conflict_orders = Order.query.filter(Order.begin_date <= end_date, Order.end_date >= start_date).all()
            # 根据有冲突的订单信息,获取有冲突的房屋信息
            conflict_houses_id = [order.house_id for order in conflict_orders]
            # 判断有冲突的房屋存在,通过notin_方法,获取所有不冲突的房屋
            if conflict_houses_id:
                filter_params.append(House.id.notin_(conflict_houses_id))
        # 如果用户只选择开始日期
        if start_date:
            conflict_orders = Order.query.filter(Order.end_date >= start_date).all()
            conflict_houses_id = [order.house_id for order in conflict_orders]
            if conflict_houses_id:
                filter_params.append(House.id.notin_(conflict_houses_id))
        # 如果用户只选择了结束日期
        if end_date:
            conflict_orders = Order.query.filter(Order.begin_date <= end_date).all()
            conflict_houses_id = [order.house_id for order in conflict_orders]
            if conflict_houses_id:
                filter_params.append(House.id.notin_(conflict_houses_id))
        # 根据sort_key的排序条件进行查询数据
        # 按照房屋成交信息进行排序
        if 'booking' == sort_key:
            houses = House.query.filter(*filter_params).order_by(House.order_count.desc())
        # 按照房屋价格进行升序排序
        elif 'price-inc' == sort_key:
            houses = House.query.filter(*filter_params).order_by(House.price.asc())
        # 按价格进行升序排序
        elif 'price-des' == sort_key:
            houses = House.query.filter(*filter_params).order_by(House.price.desc())
        # 默认按照房屋发布时间进行排序
        else:
            houses = House.query.filter(*filter_params).order_by(House.create_time.desc())
        # 对查询结果进行分页操作,page为分页的页数,每页的数据,False表示分页如果出错,不会报错
        houses_page = houses.paginate(page, constants.HOUSE_LIST_PAGE_CAPACITY, False)
        # 获取分页后的房屋数据
        houses_list = houses_page.items
        # 获取分页后的总页数
        total_page = houses_page.pages
        # 获取房屋的基本信息
        houses_dict_list = []
        for house in houses_list:
            houses_dict_list.append(house.to_basic_dict())
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询房屋列表信息异常')
    # 构造响应数据
    resp = {"errno": RET.OK, "errmsg": "OK",
            "data": {"houses": houses_dict_list, "total_page": total_page, "current_page": page}}
    # 序列化数据
    # return json.dumps(resp)
    resp_json = json.dumps(resp)
    # 判断页数是小于等于总页数
    if page <= total_page:
        # 构建redis_key
        redis_key = "houses_%s_%s_%s_%s" % (area_id, start_date_str, end_date_str, sort_key)
        # 构造操作redis数据库的事务对象
        pip = redis_store.pipeline()
        try:
            # 开启事务
            pip.multi()
            # 保存数据
            pip.hset(redis_key, page, resp_json)
            # 设置过期时间
            pip.expire(redis_key, constants.HOME_PAGE_DATA_REDIS_EXPIRES)
            # 执行事务
            pip.execute()
        except Exception as e:
            current_app.logger.error(e)
    # 返回结果
    return resp_json



