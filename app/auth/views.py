# 蓝本中的路由和视图函数
from flask import render_template,redirect,request,url_for,flash
# 退出路由,登录  确认用户的账户
from flask_login import logout_user,login_user,login_required,current_user
from . import auth
from .forms import LoginForm ,RegistrationForm,ChangePasswordForm,\
    PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm
from .. import db
from .. models import User
# 发送确认邮件
from ..email import send_email


# before_app_request 处理程序中过滤未确认的账户
@auth.before_app_request
def before_request():
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.endpoint[:5] != 'auth.'\
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url('main.index'))
    return render_template('auth/unconfirmed.html')


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

# 用户注册路由
@auth.route('/register',methods=['GET','POST'])
def register():
    # 实例化注册验证表单
    form = RegistrationForm()
    # 是否验证通过
    if form.validate_on_submit():
        # 根据新用户输入信息，实例化用户对象
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        # 保存到session域
        db.session.add(user)
        # 数据库提交
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email,'Confirm Your Account',
                'auth/email/confirm',user=user,token=token)
        flash('A Confirmation email has been sent to you by email.')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html',form=form)



# 确认用户的账户
@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed you account. Thanks!')
    else:
        flash('The Confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))


# 重新发送账户确认邮件
@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email,'Confirm Your Account',
        'auth/email/confirm',user=current_user,token=token)
    flash('A new Confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash('Your password has been updated.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password.')
    return render_template("auth/change_password.html", form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, 'Reset Your Password',
                       'auth/email/reset_password',
                       user=user, token=token,
                       next=request.args.get('next'))
        flash('An email with instructions to reset your password has been '
              'sent to you.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.password.data):
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, 'Confirm your email address',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash('An email with instructions to confirm your new email '
                  'address has been sent to you.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.')
    return render_template("auth/change_email.html", form=form)


@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('Your email address has been updated.')
    else:
        flash('Invalid request.')
    return redirect(url_for('main.index'))
