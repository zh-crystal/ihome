# coding:utf-8
import redis


class Config(object):
    """配置类"""

    SECRET_KEY = 'dqghrey43y42[-f-qagvq3'
    # 数据库（mysqlclient，flask-sqlalchemy）
    SQLALCHEMY_DATABASE_URI = 'mysql://python:pythonmysql@127.0.0.1:3306/ihome'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # 缓存（redis）
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    # 会话存储到redis中（flask-session）
    SESSION_TYPE = 'redis'
    SESSION_REDIS = redis.StrictRedis(host='127.0.0.1', port=6379, password='redis')  # 可以与缓存redis不同
    SESSION_USE_SIGNER = True  # 隐藏cookie中的session_id
    PERMANENT_SESSION_LIFETIME = 86400  # session有效期，单位s


class DevelopmentConfig(Config):
    """开发环境的配置信息"""

    DEBUG = True


class ProductionConfig(Config):
    """生产环境的配置信息"""

    pass


CONFIG_MAP = {
    "develop": DevelopmentConfig,
    "product": ProductionConfig
}
