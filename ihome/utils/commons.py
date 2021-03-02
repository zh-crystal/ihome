# coding:utf-8
import functools

from werkzeug.routing import BaseConverter
from flask import session, jsonify, g

from ihome.utils.response_code import RET


class ReConverter(BaseConverter):
    """定义正则转换器"""

    def __init__(self, url_map, regex):
        super(ReConverter, self).__init__(url_map)
        self.regex = regex


def login_required(view_func):
    """自定义验证登录装饰器"""

    @functools.wraps(view_func)  # 恢复被装饰函数的属性
    def wrapper(*args, **kwargs):
        """验证登录"""

        user_id = session.get('user_id')
        if user_id is not None:
            g.user_id = user_id  # 仅在视图函数中使用g对象存储user_id
            return view_func(*args, **kwargs)
        else:
            return jsonify(errno=RET.SESSIONERR, errmsg=u'用户未登录')
    return wrapper
