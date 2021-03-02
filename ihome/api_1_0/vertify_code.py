# coding:utf-8
import random

from flask import current_app, jsonify, make_response, request

from . import api
from ihome.utils.captcha.captcha import captcha
from ihome.utils.response_code import RET
from ihome import redis_store, constants
from ihome.models import User
from ihome.tasks.task_sms import send_sms


# GET /api/v1.0/image_codes/<image_code_id>
@api.route('/image_codes/<image_code_id>')
def get_image_code(image_code_id):
    """获取图片验证码
    :params image_code_id: 图片验证码编号
    :return: 正常：验证码图片
            异常：json
    """

    # 接收参数和检验参数已由路由完成
    # 业务逻辑处理
    name, text, image_data = captcha.generate_captcha()  # 使用工具包生成验证码图片
    try:
        # 保存到redis
        redis_store.setex("image_code_%s" % image_code_id,
                          constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=u"保存图片验证码异常")
    # 返回响应
    resp = make_response(image_data)
    resp.headers["Content-Type"] = "image/jpg"
    return resp


# GET /api/v1.0/sms_codes/<mobile>?image_code=xxx&image_code_id=xxx
@api.route("/sms_codes/<re('1[34578]\\d{9}'):mobile>")
def get_sms_code(mobile):
    """获取短信验证码
    :params mobile: 手机号
    :return: 正常：短信验证码
            异常：json
    """

    # 接收参数
    image_code = request.args.get('image_code')
    image_code_id = request.args.get('image_code_id')

    # 校验参数
    if not all([image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg=u"参数不完整")

    # 业务逻辑处理
    # 1. 校验图片验证码
    try:
        real_image_code = redis_store.get('image_code_%s' % image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=u'校验图片验证码异常')
    if real_image_code is None:
        return jsonify(errno=RET.NODATA, errmsg=u'图片验证码失效')
    try:
        # 删除过期或已尝试验证的图片验证码
        redis_store.delete('image_code_%s' % image_code_id)
    except Exception as e:
        current_app.logger.error(e)
    if real_image_code.lower() != image_code.lower():
        return jsonify(errno=RET.DATAERR, errmsg=u'图片验证码错误')

    # 2. 校验手机号是否已注册
    # 判断手机号60s内是否有发送记录，防止频繁触发
    try:
        send_flag = redis_store.get("send_sms_code_%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if send_flag is not None:
            return jsonify(errno=RET.REQERR, errmsg=u'请求过于频繁，60s后重试')
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
    else:
        if user is not None:
            return jsonify(errno=RET.DATAEXIST, errmsg=u'手机号已注册')

    # 3. 生成短信验证码并保存到redis
    sms_code = "%06d" % random.randint(0, 999999)
    try:
        redis_store.setex("sms_code_%s" % mobile,
                          constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # 保存发送记录，方式60s内再次触发
        redis_store.setex("send_sms_code_%s" % mobile,
                          constants.SEND_SMS_CODE_INTERVAL, 1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=u"保存短信验证码异常")

    # 4. 发送短信验证码
    # 使用celery异步发送
    send_sms.delay(mobile, [sms_code, int(constants.SMS_CODE_REDIS_EXPIRES/60)], 1)

    # 返回响应
    return jsonify(errno=RET.THIRDERR, errmsg=u"发送失败")
