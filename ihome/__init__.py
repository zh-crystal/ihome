# coding:utf-8
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_wtf import CSRFProtect
import redis

from config import CONFIG_MAP
from ihome.utils.commons import ReConverter


db = SQLAlchemy()  # 数据库连接
redis_store = None  # redis缓存连接


# 配置日志信息
# 全局logger对象可以通过标准模块logging取得也可以通过flask.current_app.logger取得
logging.basicConfig(level=logging.INFO)  # 设置日志的记录等级，flask的debug模式会忽略该设置
file_log_handler = RotatingFileHandler(
    "logs/log", maxBytes=1024*1024*10, backupCount=10)  # 创建日志记录器
file_log_handler.setFormatter(
    logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
)  # 创建日志记录的格式
logging.getLogger().addHandler(file_log_handler)  # 注册日志记录器到全局日志对象


# 工厂模式
def create_app(config_name):
    """创建flask应用对象
    :param config_name: str 配置模式名称 ["develop","product"]
    :return: Flask instance
    """

    app = Flask(__name__)

    # 区分配置环境
    config_cls = CONFIG_MAP.get(config_name)
    app.config.from_object(config_cls)

    '''flask扩展都遵循两种方式
        1. db = SQLAlchemy(app)
        2. db = SQLAlchemy()
           db.init_app(app)
    '''
    db.init_app(app)  # 初始化数据库

    # 先在全局定义为None以便其它模块导入，创建应用时再初始化
    global redis_store
    redis_store = redis.StrictRedis(host=config_cls.REDIS_HOST,
                                    port=config_cls.REDIS_PORT,
                                    password="redis")  # 初始化缓存redis

    # flask应用补充操作，使用时不需要额外导入，也就不需要全局定义
    Session(app)  # 配置session
    CSRFProtect(app)  # csrf防护（仅验证），使用请求钩子实现类似django中间件的功能

    # 添加自定义转换器
    app.url_map.converters['re'] = ReConverter

    # 注册蓝图
    from ihome import api_1_0, web_html  # 推迟导入，避免循环导入
    app.register_blueprint(api_1_0.api, url_prefix='/api/v1.0')
    app.register_blueprint(web_html.html)

    return app
