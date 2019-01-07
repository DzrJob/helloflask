from . import db

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
    # 定义外键role_id 关联Role的主键roles.id
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username
