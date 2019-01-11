# from flask import render_template, session, redirect, url_for, current_app
# from .. import db
# from ..models import User
# from ..email import send_email
# from .forms import NameForm

# # 支持请求
# @main.route('/', methods=['GET', 'POST'])
# def index():
#     form = NameForm()
#     # 验证表单
#     if form.validate_on_submit():
#         # 数据库查找
#         user = User.query.filter_by(username=form.name.data).first()
#         # 用户不存在
#         if user is None:
#             # 实例化用户
#             user = User(username=form.name.data)
#             # 存入数据库
#             db.session.add(user)
#             session['known'] = False
#             # 如果管理员存在
#             if current_app.config['FLASKY_ADMIN']:
#                 # 发送邮件给管理员 地址 主题 模板路径 解包
#                 send_email(current_app.config['FLASKY_ADMIN'], 'New User',
#                         # 应用模板
#                         'mail/new_user', user=user)
#         else:
#             session['known'] = True
#         session['name'] = form.name.data
#         # 重定向 反向解析 .当前app中index函数
#         return redirect(url_for('.index'))
#         # return redirect(revers,'main:index')
#     # 渲染
#     return render_template('index.html',
#             form=form,name=session.get('name'),
#             known=session.get('known',False))

from flask import render_template
from . import main

# 支持请求
@main.route('/')
def index():
    # 渲染
    return render_template('index.html')
