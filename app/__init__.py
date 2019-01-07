from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import config

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()

# 实例化app
def create_app(config_name):
    app = Flask(__name__)
    # 应用配置文件
    app.config.from_object(config[config_name])
    # 应用配置启用app
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)

    # 蓝本
    from .main import main as main_blueprint
    # install app 添加应用到主路由
    app.register_blueprint(main_blueprint)
    # 前缀
    # app.register_blueprint(main_blueprint，url_prefix='/app_1')
    return app

