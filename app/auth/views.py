# 蓝本中的路由和视图函数
from flask import render_template,redirect,request,url_for,flash
from . import auth
from .. models import User
from .forms import LoginForm
# 退出路由,登录  确认用户的账户
from flask_login import logout_user,login_user,login_required,current_user
# 发送确认邮件
from ..email import send_email


# # before_app_request 处理程序中过滤未确认的账户
# @auth.before_app_request
# def before_request():
#     if current_user.is_authenticated \
#             and not current_user.confirmed \
#             and request.endpoint[:5] != 'auth.'\
#             and request.endpoint != 'static':
#         return redirect(url_for('auth.unconfirmed'))


# @auth.route('/unconfirmed')
# def unconfirmed():
#     if current_user.is_anonymous() or current_user.confirmed:
#         return redirect(url('main.index'))
#     return render_template('auth/unconfirmed.html')


# 用户登录
@auth.route('/login',methods=['GET','POST'])
def login():
    # 实例化登录验证表单
    form = LoginForm()
    # 验证是否通过
    if form.validate_on_submit():
        # 根据用户输入的email过滤
        user = User.query.filter_by(email=form.email.data).first()
        # 如果用户不为空且输入密码对比通过
        # verify_password()将参数传给Werkzeug的password_hash(),与User模型中
        # 密码散列值进行对比
        if user is not None and user.verify_password(form.password.data):
            # 参数是要登录的用户，以及可选remember_me也在表单中填写
            login_user(user,form.remember_me.data)
            # 返回原地址或者主页
            # 从 request.args 字典中next 读取存储的原地址
            return redirect(request.args.get('next') or url_for('main.index'))
        # 否则提示错误消息
        flash('Invalid username or password.')
    # 渲染登录页面
    return render_template('auth/login.html',form=form)

@auth.route('/logout')
# 如果未认证的用户访问这个路由，Flask-Login 会拦截请求，把用户发往登录页面
@login_required
def logout():
    # 删除并重设用户回话
    logout_user()
    # 消息
    flash('You have been logged out.')
    # 重定向到首页
    return redirect(url_for('main.index'))

# # 用户注册路由
# @auth.route('/register',methods=['GET','POST'])
# def register():
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         user = User(email=form.email.data,
#                     username=form.username.data,
#                     password=form.password.data)
#         db.session.add(user)
#         db.session.commit()
#         token = user.generate_confirmation_token()
#         send_email(user.email,'Confirm Your Account',
#                 'auth/email/Confirm',user=user,token=token)
#         flash('A Confirmation email has been sent to you by email.')
#         return redirect(url_for('main.index'))
#     return render_template('auth/register.html',form=form)


# # 确认用户的账户
# @auth.route('/Confirm/<token>')
# @login_required
# def confirm(token):
#     if current_user.confirmed:
#         return redirect(url_for('main.index'))
#     if current_user.confirm(token):
#         flash('You have confirmed you account. Thanks!')
#     else:
#         flash('The Confirmation link is invalid or has expired.')
#     return redirect(url_for('main.index'))


# # 重新发送账户确认邮件
# @auth.route('/confirm')
# @login_required
# def resend_confirmation():
#     token = current_user.generate_confirmation_token()
#     send_email(current_user.email,'Confirm Your Account',
#         'auth/email/Confirmation',user=current_user,token=token)
#     flash('A new Confirmation email has been sent to you by email.')
#     return redirect(url_for('main.index'))
