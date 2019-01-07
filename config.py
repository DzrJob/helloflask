import os
# 绝对路径
basedir = os.path.abspath(os.path.dirname(__file__))

# 配置文件 基类
class Config:
    # 跨站请求伪造保护
    # Flask-WTF 需要程序设置一个密钥
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    # 每次请求结束后都会自动提交数据库中的变动。
    # 自动提交
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    # 是否追踪对象的修改并且发送信号。
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 邮件配置
    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 25
    MAIL_USE_TLS = False
    # 应用系统中的环境变量
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    # 发送邮件的邮件标题头
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    # 邮件发送人
    FLASKY_MAIL_SENDER = 'Flasky Admin <dzr_job@163.com>'
    # 管理员
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')

    @staticmethod
    def init_app(app):
        pass

# 开发环境
class DevelopmentConfig(Config):
    DEBUG = True
    # 数据库定位
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
            'sqlite:///' + os.path.join(basedir,'data-dev.sqlite')

 # 测试环境
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
            'sqlite:///' + os.path.join(basedir,'data-test.sqlite')

# 生产环境
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or \
            'sqlite:///' + os.path.join(basedir,'data.sqlite')


config = {
        'development': DevelopmentConfig,
        'testing': TestingConfig,
        'production': ProductionConfig,
        'default': DevelopmentConfig
        }

