from . import db
# 模型中加入密码散列 注册用户 验证用户
from werkzeug.security import generate_password_hash, check_password_hash

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


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    # hash密码
    password_hash = db.Column(db.String(128))

    # 定义外键role_id 关联Role的主键roles.id
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username

    # getter密码不可读
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    # setter密码设置密码 加密方法和盐值默认
    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)

    # 散列密码与输入密码匹配验证
    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)


