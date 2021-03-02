# coding:utf-8
from ihome import create_app, db
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand


if __name__ == '__main__':
    app = create_app("develop")  # 创建Flask应用对象

    Migrate(app, db)  # 数据库迁移

    manager = Manager(app)  # flask-script扩展脚本
    manager.add_command('db', MigrateCommand)  # 添加迁移命令
    
    manager.run()  # 以扩展脚本形式运行
