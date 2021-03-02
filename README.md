[env]
    WSL2-Ubuntu20.04
    python2.7
    requirements.txt


[service]
    数据库：mysql8.0

    缓存、会话：redis

    图片验证码：captcha
        对接方式：ihome/utils/captcha，使用captcha工具

    短信验证码：容量云通讯
        对接方式：ihome/lib/yuntongxun，自定义sms.py

    图片存储：FastDFS
        对接方式：安装FastDFS、nginx
            pip install fdfs_client-py
            ihome/utils/fdfs
        上传和获取都依赖nginx，仅在上传时需要启动机器上的fast-trackerd、fdfs-storaged
    
    多任务：celery
        对接方式：pip install celery
        celery版本需要与redis（pip安装的redis包）版本协调
    
    支付：alipay（沙箱环境）
        对接方式：pip install alipay-python-sdk
            需要使用本地私钥和支付宝公钥：ihome/api_1.0/keys


[plugins]
    前端js模板：art-template
        对接方式：在html中引入ihome/static/js/template.js
    
    前端表单异步提交：jquery-form
        对接方式：在html中引入ihome/static/js/jquery-form.min.js


[tree]
    .
    ├── README.md
    ├── config.py
    ├── ihome
    │   ├── __init__.py
    │   ├── api_1_0
    │   │   ├── __init__.py
    │   │   ├── demo.py
    │   │   ├── passport.py
    │   │   ├── profile.py
    │   │   ├── vertify_code.py
    │   ├── constants.py
    │   ├── libs
    │   │   ├── __init__.py
    │   │   └── yuntongxun
    │   │       ├── CCPRestSDK.py
    │   │       ├── __init__.py
    │   │       ├── sms.py
    │   │       ├── xmltojson.py
    │   ├── models.py
    │   ├── static
    │   │   ├── css
    │   │   │   ├── ihome
    │   │   ├── favicon.ico
    │   │   ├── html
    │   │   ├── images
    │   │   ├── js
    │   │   │   ├── ihome
    │   │   └── plugins
    │   │       ├── bootstrap
    │   │       ├── bootstrap-datepicker
    │   │       ├── bootstrap-switch
    │   │       ├── font-awesome
    │   │       ├── simple-line-icons
    │   │       ├── swiper
    │   │       └── uniform
    │   ├── utils
    │   │   ├── __init__.py
    │   │   ├── captcha
    │   │   │   ├── __init__.py
    │   │   │   ├── captcha.py
    │   │   │   └── fonts
    │   │   ├── commons.py
    │   │   ├── fdfs
    │   │   │   ├── __init__.py
    │   │   │   ├── client.conf
    │   │   │   ├── image_store.py
    │   │   ├── response_code.py
    │   ├── web_html.py
    ├── logs
    ├── manage.py
    ├── migrations
    │   └── versions
    └── requirements.txt


[script]
    启动：python manage.py runserver

    数据库迁移：python manage.py db [MigrateCOmmand]
        [MigrateCOmmand]
            init 初始化
            migrate -m 'info' 生成迁移文件
            upgrade 执行迁移（升级）
            history 查看版本
            downgrade [version] 降级迁移
        [version]
            通常为迁移文件前缀，可通过history查看

