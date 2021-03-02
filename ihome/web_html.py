# coding:utf-8
from flask import Blueprint, current_app, make_response
from flask_wtf import csrf

# 提供静态文件的蓝图
html = Blueprint('web_html', __name__)


# /html_filename
@html.route("/<re(r'.*'):html_filename>")
def get_html(html_filename):
    """提供静态html文件"""

    # 拼接资源uri
    if not html_filename:
        html_filename = 'index.html'
    if html_filename != 'favicon.ico':
        html_filename = 'html/' + html_filename
    # 设置cookie中的csrf_token
    csrf_token = csrf.generate_csrf()
    resp = make_response(current_app.send_static_file(html_filename))
    resp.set_cookie('csrf_token', csrf_token)
    return resp
