# coding:utf-8
import re

from flask import request, jsonify, current_app, session
from sqlalchemy.exc import IntegrityError

from . import api
from ihome.utils.response_code import RET
from ihome import redis_store, db, constants
from ihome.models import User


# POST /api/v1.0/users 
# 请求参数：{手机号、短信验证码、密码、重复密码}，json
@api.route("/users", methods=["POST"])
def register():
    """注册"""

    # 获取参数
    req_dict = request.get_json()
    mobile = req_dict.get("mobile")
    sms_code = req_dict.get("sms_code")
    password = req_dict.get("password")
    password2 = req_dict.get("password2")

    # 校验参数
    # 1. 参数完整性
    if not all([mobile, sms_code, password, password2]):
        return jsonify(errno=RET.PARAMERR, errmsg=u"参数不完整")
    # 2. 手机号
    if not re.match(r"1[34578]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg=u"手机号格式错误")
    # 3. 密码
    if password != password2:
        return jsonify(errno=RET.PARAMERR, errmsg=u"两次密码不一致")
    # 4. 短信验证码
    try:
        real_sms_code = redis_store.get("sms_code_%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=u"读取短信验证码异常")
    if real_sms_code is None:
        return jsonify(errno=RET.NODATA, errmsg=u"短信验证码失效")
    try:
        # 删除redis中的短信验证码，防止重复使用校验
        redis_store.delete("sms_code_%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)
    if real_sms_code != sms_code:
        return jsonify(errno=RET.DATAERR, errmsg=u"短信验证码错误")

    # 业务处理
    # 1. 保存用户的注册数据到数据库中
    user = User(name=mobile, mobile=mobile)
    user.password = password  # 设置属性，调用模型类中password.setter装饰方法
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:
        # 模型类中设置mobile为unique，因此手机号若存在会在保存时抛出异常
        db.session.rollback()  # 回滚到异常commit提交前的状态
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAEXIST, errmsg=u"手机号已存在")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=u"查询数据库异常")
    # 2. 保存登录状态到session中
    session["name"] = mobile
    session["mobile"] = mobile
    session["user_id"] = user.id

    # 返回结果
    return jsonify(errno=RET.OK, errmsg=u"注册成功")


# POST /api/v1.0/sessions
# 请求参数：{手机号、密码} json
@api.route('/sessions', methods=['POST'])
def login():
    """用户登录"""

    # 获取参数
    req_dict = request.get_json()
    mobile = req_dict.get("mobile")
    password = req_dict.get("password")

    # 校验参数
    # 1. 参数完整的校验
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg=u"参数不完整")
    # 2. 手机号
    if not re.match(r"1[34578]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg=u"手机号格式错误")
    user_ip = request.remote_addr  # 用户的ip地址
    try:
        # redis记录： "access_nums_请求的ip": "次数"
        access_nums = redis_store.get("access_num_%s" % user_ip)
    except Exception as e:
        current_app.logger.error(e)
    else:
        # 限制ip访问次数
        if access_nums is not None and int(access_nums) >= constants.LOGIN_ERROR_MAX_TIMES:
            return jsonify(errno=RET.REQERR, errmsg=u"错误次数过多，十分钟后重试")
    # 3. 密码
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=u"获取用户信息失败")
    if user is None or not user.check_password(password):
        try:
            # incr：对字符串类型的数字数据进行加一操作，
            # 如果数据一开始不存在，则会先初始化为0再加一
            redis_store.incr("access_num_%s" % user_ip)
            redis_store.expire("access_num_%s" % user_ip, constants.LOGIN_ERROR_FORBID_TIME)
        except Exception as e:
            current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg=u"用户名或密码错误")

    # 业务处理
    # 如果验证相同成功，保存登录状态， 在session中
    session["name"] = user.name
    session["mobile"] = user.mobile
    session["user_id"] = user.id

    # 返回响应
    return jsonify(errno=RET.OK, errmsg=u"登录成功")


# GET /api/v1.0/session
@api.route("/session", methods=["GET"])
def check_login():
    """检查登陆状态"""

    # 尝试从session中获取用户的名字
    name = session.get("name")
    # 如果session中数据name名字存在，则表示用户已登录，否则未登录
    if name is not None:
        return jsonify(errno=RET.OK, errmsg="true", data={"name": name})
    else:
        return jsonify(errno=RET.SESSIONERR, errmsg="false")


# DELETE /api/v1.0/session
@api.route("/session", methods=["DELETE"])
def logout():
    """登出"""

    # 清除session数据
    csrf_token = session.get("csrf_token")
    session.clear()

    # 防止flask-session设置在redis中的csrf被清除
    # 导致flask-wtf无法从session取csrf
    session["csrf_token"] = csrf_token  
    return jsonify(errno=RET.OK, errmsg="OK")
