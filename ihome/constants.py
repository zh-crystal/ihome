# coding:utf-8


IMAGE_CODE_REDIS_EXPIRES = 180  # 图片验证码有效期（秒）
SMS_CODE_REDIS_EXPIRES = 300  # 短信验证码有效期（秒）
SEND_SMS_CODE_INTERVAL = 60  # 发送短信验证码的间隔
LOGIN_ERROR_MAX_TIMES = 5  # 登录错误尝试次数
LOGIN_ERROR_FORBID_TIME = 600  # 登录错误限制的时间（秒）
FDFS_URL_DOMAIN = 'http://127.0.0.1:8888/'  # 存储系统/服务文件url域名，此处使用FDFS
AREA_INFO_REDIS_CACHE_EXPIRES = 7200  # 城区信息的缓存时间, 单位：秒
HOME_PAGE_MAX_HOUSES = 5  # 首页展示最多的房屋数量
HOME_PAGE_DATA_REDIS_EXPIRES = 7200  # 首页房屋数据的Redis缓存时间，单位：秒
HOUSE_DETAIL_COMMENT_DISPLAY_COUNTS = 30  # 房屋详情页展示的评论最大数
HOUSE_DETAIL_REDIS_EXPIRE_SECOND = 7200  # 房屋详情页面数据Redis缓存时间，单位：秒
HOUSE_LIST_PAGE_CAPACITY = 2  # 房屋列表页面每页数据容量
HOUES_LIST_PAGE_REDIS_CACHE_EXPIRES = 7200  # 房屋列表页面页数缓存时间，单位秒
ALIPAY_URL_PREFIX = "https://openapi.alipaydev.com/gateway.do?"  # 支付宝的网关地址（支付地址域名）
