from . import db,login_manager
# 模型中加入密码散列 生成密码 验证密码
from werkzeug.security import generate_password_hash, check_password_hash
# Flask-Login User 模型默认实现用户方法
# is_authenticated 如果用户已经登录，必须返回 True，否则返回 False
# is_active 如果允许用户登录，必须返回 True，否则返回 False。如果要禁用账户，可以返回 False
# is_anonymous 对普通用户必须返回 False
# get_id 必须返回用户的唯一标识符，使用 Unicode 编码字符串
from flask_login import UserMixin ,AnonymousUserMixin
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

    default = db.Column(db.Boolean,default=False,index=True)
    # 权限
    permissions = db.Column(db.Integer)

    # 返回一个具有可读性的字符串，表示模型
    def __repr__(self):
        return '<Role %r>' % self.name

    #管理员 0b11111111（0xff） 具有所有权限，包括修改其他用户所属角色的权限
    @staticmethod
    def insert_roles():
        roles = {
            'User':(
                Permission.FOLLOW |
                Permission.COMMENT |
                Permission.WRIT_ARTICLES , True
            ),
            'Moderator':(
                Permission.FOLLOW |
                Permission.COMMENT |
                permissions.WRIT_ARTICLES |
                permissions.MODERATE_COMMENTS,False
            ),
            'Administrator':(0xff,False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

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

    # 角色添加
    def __init__(self,**kwargs):
        super(User,self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['Flask-Admin']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = role.query.filter_by(default=True).first()

    def can(self,permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

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

    # 生成令牌方法，有效期1小时
    def generate_confirmation_token(self,expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'confirm':self.id})

    # 检验令牌方法
    def confirm(self,token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True


    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True


    def __repr__(self):
        return '<User %r>' % self.username

# 程序权限
class Permission:
    # 关注用户
    FOLLOW = 0x01
    # 评论文章
    COMMENT = 0x02
    # 发表文章
    WRIT_ARTICLES = 0x04
    # 评论处理权限
    MODERATE_COMMENTS = 0x08
    # 管理员权限
    ADMINISTER = 0x80


class AnonymousUser(AnonymousUserMixin):
    def can(self,permissions):
        return False
    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser

# 加载用户的回调函数
# 找到返用户对象否则返回None
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
