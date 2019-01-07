import os
from app import create_app, db
from app.models import User, Role
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
# create_app() 函数就是程序的工厂函数，接受一个参数，是程序使用的配置名。
# 创建app应用配置文件 或默认的
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
# Manager类追踪所有在命令行中调用的命令和处理过程的调用运行情况
manager = Manager(app)
# 迁移
migrate = Migrate(app, db)


# python manage.py shell 注入到环境
def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)
# 将shell命令加入Manager实例
manager.add_command('shell', Shell(make_context=make_shell_context))
# 导出数据库迁移命令 MigrateCommand 类使用 db 命令附加 到 manager 对象
manager.add_command('db', MigrateCommand)
# init 子命令创建迁移仓库
# (venv) $ python hello.py db init
# migrate 子命令用来自动创建迁移脚本
# (venv) $ python hello.py db migrate -m "initial migration"
# 检查并修正好迁移脚本之后，我们可以使用 db upgrade 命令把迁移应用到数据库中
# (venv) $ python hello.py db upgrade


# python manage.py test
@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoder().discover('tests')
    unittest.TestTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
    manager.run()
