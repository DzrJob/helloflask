from . import db,login_manager
# 模型中加入密码散列 生成密码 验证密码
from werkzeug.security import generate_password_hash, check_password_hash
# Flask-Login User 模型默认实现用户方法
# is_authenticated() 如果用户已经登录，必须返回 True，否则返回 False
# is_active() 如果允许用户登录，必须返回 True，否则返回 False。如果要禁用账户，可以返回 False
# is_anonymous() 对普通用户必须返回 False
# get_id() 必须返回用户的唯一标识符，使用 Unicode 编码字符串
from flask_login import UserMixin
# 加载用户的回调函数
from . import login_manager
# 确认用户账户
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app


# 定义模型
class Role(db.Model):
    # 定义在数据库中使用的表名
    __tablename__ = 'roles'
    # 类构造函数的第一个参数是数据库列和模型属性的类型其余的参数指定属性的配置选项。
    # 整数型 主键
    id = db.Column(db.Integer, primary_key=True)
    # 字符串 唯一
    name = db.Column(db.String(64), unique=True)
    # 关联用户表
    # 关联的模型 backref定义反向关系 lazy如何加载相关记录 dynamic（不加载记录，但提供加载记录的查询）
    users = db.relationship('User', backref='role', lazy='dynamic')
    # 返回一个具有可读性的字符串，表示模型
    def __repr__(self):
        return '<Role %r>' % self.name

# UserMixin 多重继承 默认实现用户方法
class User(UserMixin,db.Model):
    # 表名
    __tablename__ = 'users'
    # id
    id = db.Column(db.Integer, primary_key=True)
    # email
    email = db.Column(db.String(64),unique=True,index=True)
    # 用户名
    username = db.Column(db.String(64), unique=True, index=True)
    # 加密密码
    password_hash = db.Column(db.String(128))

    confirmed = db.Column(db.Boolean,default=False)

    # 定义外键role_id 关联Role的主键roles.id
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username

    # getter 密码不可读
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    # setter 加密密码
    # generate_password_hash(password, method=pbkdf2:sha1, salt_length=8)
    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)

    # 密码验证
    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)

    # # 生成令牌方法，有效期1小时
    # def generate_confirmation_token(self,expiration=3600):
    #     s = Serializer(current_app.config['SECRET_KEY'],expiration)
    #     return s.dumps({'confirm':self.id})

    # # 检验令牌方法
    # def confirm(self,token):
    #     s = Serializer(current_app.config['SECRET_KET'])
    #     try:
    #         data = s.loads(token)
    #     except:
    #         return False
    #     if data.get('confirm') != self.id:
    #         return False
    #     self.confirmed = True
    #     db.session.add(self)
    #     return True

    def __repr__(self):
        return '<User %r>' % self.username

# 加载用户的回调函数
# 找到返用户对象否则返回None
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
