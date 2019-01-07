#coding=utf-8
import os
from threading import Thread
# 初始化Flask 渲染模板
from flask import Flask, render_template, session, redirect, url_for
from flask_script import Manager, Shell
# 用户界面组件
from flask_bootstrap import Bootstrap
# 获取用户电脑中的时区和区域设置
from flask_moment import Moment
# Flask-WTF 能保护所有表单免受跨站请求伪造
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.validators import Required
# 管理数据库
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate,MigrateCommand
# 初始化Flask-Mail
from flask_mail import Mail,Message


# 绝对路径
basedir = os.path.abspath(os.path.dirname(__file__))

# 初始化创建Falsk实例，参数为主模块或包的名字
app = Flask(__name__)
# 配置文件 app.config 字典可用来存储框架、扩展和程序本身的配置变量。
# 跨站请求伪造保护
# Flask-WTF 需要程序设置一个密钥
app.config['SECRET_KEY'] = 'hard to guess string'
# 配置数据库
# 数据库 URL 必须保存到 Flask 配置对象的 SQLALCHEMY_DATABASE_URI 键中
# database 表示要使用的数据库名。
app.config['SQLALCHEMY_DATABASE_URI']=\
    'sqlite:///'+os.path.join(basedir,'data.sqlite')
# 每次请求结束后都会自动提交数据库中的变动。
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
# 是否追踪对象的修改并且发送信号。
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 邮箱
app.config['MAIL_SERVER'] = 'smtp.163.com'
#app.config['MAIL_PORT'] = 587
#app.config['MAIL_USE_TLS'] = True
app.config['MAIL_PORT'] = 25
# 加密
app.config['MAIL_USE_TLS'] = False
# 应用系统中的环境变量
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
# 发送邮件的邮件标题头
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
# 邮件发送人
app.config['FLASKY_MAIL_SENDER'] = 'Flasky Admin <dzr_job@163.com>'
# 管理员
app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')
# 添加进环境变量
#(venv) $ export MAIL_USERNAME=<Gmail username>
#(venv) $ export MAIL_PASSWORD=<Gmail password>


# 命令行
manager = Manager(app)
# 模板
bootstrap = Bootstrap(app)
# 时间
moment = Moment(app)
# 数据库
db = SQLAlchemy(app)
# 邮箱
mail = Mail(app)

# 迁移
migrate = Migrate(app,db)


# 定义模型
class Role(db.Model):
    # 定义在数据库中使用的表名
    __tablename__ = 'roles'
    # db.Column 类构造函数的第一个参数是数据库列和模型属性的类型。
    # 其余的参数指定属性的配置选项。
    # 整数型 主键
    id = db.Column(db.Integer, primary_key=True)
    # 字符串 唯一
    name = db.Column(db.String(64), unique=True)
    # 关联用户表
    # users 属性将返回与角色相关联的用户组成的列表。
    # 第一个参数表明这个关系的另一端是哪个模型
    # 额外参数，从而确定所用外键。
    # backref 参数向 User 模型中添加一个 role 属性，从而定义反向关系。
    # lazy 指定如何加载相关记录 dynamic（不加载记录，但提供加载记录的查询）
    users = db.relationship('User', backref='role', lazy='dynamic')

    # 返回一个具有可读性的字符串，表示模型
    def __repr__(self):
        return '<Role %r>' % self.name

# 定义模型
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    # 定义外键role_id 关联Role的主键roles.id
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username

# 异步发送邮件
def send_async_email(app,msg):
    with app.app_context():
        mail.send(msg)

# 发送邮件
def send_email(to,subject,template,**kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + '' + subject,
            sender = app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email,args=[app,msg])
    thr.start()
    return thr

# 定义表单类
class NameForm(FlaskForm):
    name = StringField('What is you name?', validators=[Required()])
    submit = SubmitField('Submit')

# 上下文环境（放入变量）shell可以直接用
def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)
manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db',MigrateCommand)

# 自定义错误页面
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404

# 自定义错误页面
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'),500

# 路由修饰器，可以多个
@app.route('/index')
# methods 参数告诉 Flask 在 URL 映射中把这个视图函数注册为GET 和 POST 请求的处理程序。
@app.route('/',methods=['GET','POST'])
# 主页视图函数
def index():
    # 实例化用户form表单
    form = NameForm()
    # 表单验证 通过True 否则 False
    if form.validate_on_submit():
        # form.name.data接收表单中的数据
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False
            if app.config['FLASKY_ADMIN']:
                send_email(app.config['FLASKY_ADMIN'],'New User',
                        'mail/new_user',user=user)
        else:
            session['known'] = True
        session['name'] = form.name.data
        # 重定向
        return redirect(url_for('index'))
    # 渲染
    return render_template('index.html', form=form, name=session.get('name'),
                                       known=session.get('known', False))

# 启动服务器
# run方法启动 Flask集成的开发 Web 服务器
if __name__ == '__main__':
    manager.run()
