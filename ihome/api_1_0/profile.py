# coding:utf-8
from flask import g, request, jsonify, current_app, session
from sqlalchemy.exc import IntegrityError

from . import api
from ihome.utils.commons import login_required
from ihome.utils.response_code import RET
from ihome.utils.fdfs.image_store import storage
from ihome.models import User
from ihome import db, constants


# POST /api/v1.0/users/avatar
# 请求参数：{图片、用户id}，多媒体表单、g对象
@api.route('/users/avatar', methods=['POST'])
@login_required
def set_user_avator():
    """设置用户头像"""

    # 获取参数
    user_id = g.user_id  # login_required将user_id存储到g对象供视图访问
    image_file = request.files.get('avatar')
    
    # 校验参数
    if image_file is None:
        return jsonify(errno=RET.PARAMERR, errmsg=u'未上传图片')
    
    # 业务处理
    # 1. 上传图片
    image_data = image_file.read()
    try:
        file_name = storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg=u'上传图片失败')
    # 2. 保存图片文件名到数据库中
    try:
        User.query.filter_by(id=user_id).update({"avatar_url": file_name})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=u'保存图片信息失败')
    # 3. 拼接图片url
    avatar_url = constants.FDFS_URL_DOMAIN + file_name

    # 返回响应
    return jsonify(errno=RET.OK, errmsg=u'保存成功', data={"avatar_url": avatar_url})


# PUT /api/v1.0/users/name
# 请求参数：{用户名}，json
@api.route("/users/name", methods=["PUT"])
@login_required
def change_user_name():
    """修改用户名"""

    # 获取和校验参数
    user_id = g.user_id
    req_data = request.get_json()
    if not req_data:
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")
    name = req_data.get("name")  # 用户想要设置的名字
    if not name:
        return jsonify(errno=RET.PARAMERR, errmsg="名字不能为空")

    # 保存用户昵称name
    try:
        User.query.filter_by(id=user_id).update({"name": name})
        db.session.commit()
    except IntegrityError as e:
        # 并同时判断name是否重复（利用数据库的唯一索引)
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DATAEXIST, errmsg=u"用户名已存在")
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="设置用户错误")
    # 修改session数据中的name字段
    session["name"] = name

    # 返回响应
    return jsonify(errno=RET.OK, errmsg="OK", data={"name": name})


# GET /api/v1.0/users/auth
@api.route("/users/auth", methods=["GET"])
@login_required
def get_user_auth():
    """获取用户的实名认证信息"""

    user_id = g.user_id

    # 在数据库中查询信息
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取用户实名信息失败")

    if user is None:
        return jsonify(errno=RET.NODATA, errmsg="无效操作")

    return jsonify(errno=RET.OK, errmsg="OK", data=user.auth_to_dict())


# POST /api/v1.0/users/auth
@api.route("/users/auth", methods=["POST"])
@login_required
def set_user_auth():
    """保存实名认证信息"""

    user_id = g.user_id

    # 获取参数
    req_data = request.get_json()
    if not req_data:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    real_name = req_data.get("real_name")  # 真实姓名
    id_card = req_data.get("id_card")  # 身份证号

    # 参数校验
    if not all([real_name, id_card]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 保存用户的姓名与身份证号
    try:
        # 字段为空才允许认证，保证只能认证一次
        User.query.filter_by(id=user_id, real_name=None, id_card=None)\
            .update({"real_name": real_name, "id_card": id_card})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存用户实名信息失败")

    return jsonify(errno=RET.OK, errmsg="OK")


# GET /api/v1.0/user
@api.route("/user", methods=["GET"])
@login_required
def get_user_profile():
    """获取个人信息"""

    user_id = g.user_id
    # 查询数据库获取个人信息
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取用户信息失败")

    if user is None:
        return jsonify(errno=RET.NODATA, errmsg="无效操作")

    return jsonify(errno=RET.OK, errmsg="OK", data=user.to_dict())
