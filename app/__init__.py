# 从flask模块导入Flask对象
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import config
# 初始化Flask-Login
from flask_login import LoginManager


bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()

# 初始化Flask-Login
login_manager = LoginManager()
# 安全等级 
login_manager.session_protection = 'strong'
# 设置登录页面的端点
login_manager.login_view = 'auth.login'


# 实例化app
def create_app(config_name):
    # 把Flask对象生成并赋给变量app
    app = Flask(__name__)
    # 应用配置文件
    app.config.from_object(config[config_name])
    # 应用配置启用app
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    # 登录
    login_manager.init_app(app)

    # 注册主路由蓝本
    from .main import main as main_blueprint
    # install app 添加应用到主路由
    app.register_blueprint(main_blueprint)
    # 注册认证蓝本（app）
    from .auth import auth as auth_blueprint
    # URL前缀
    app.register_blueprint(auth_blueprint,url_prefix='/auth')

    return app
