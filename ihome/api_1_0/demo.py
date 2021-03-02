# coding:utf-8
from flask import current_app

from ihome import db, models
from . import api


# /api/v1.0/index
@api.route('/index')
def index():
    return 'index page'
