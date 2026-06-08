from datetime import datetime, timedelta
from urllib.parse import urlparse, urljoin
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from studypilot.extensions import db
from studypilot.models import User, EmailToken, LearningPreference
from studypilot.utils import generate_token, send_verification_email, send_password_reset_email

auth_bp = Blueprint('auth', __name__)


def _is_safe_url(target):
    """验证 URL 是否为站内地址，防止开放重定向攻击."""
    if not target:
        return False
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.netloc == ref_url.netloc and test_url.scheme == ref_url.scheme


# ============================================================
# 注册
# ============================================================

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        errors = []
        if not username or len(username) < 2 or len(username) > 64:
            errors.append('用户名长度应为 2-64 个字符')
        if not email or '@' not in email:
            errors.append('请输入有效的邮箱地址')
        if len(password) < 6:
            errors.append('密码长度至少 6 位')
        if password != confirm:
            errors.append('两次输入的密码不一致')

        if User.query.filter_by(username=username).first():
            errors.append('该用户名已被注册')
        if User.query.filter_by(email=email).first():
            errors.append('该邮箱已被注册')

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('auth/register.html', username=username, email=email)

        user = User(username=username, email=email)
        user.set_password(password)
        user.is_active = False
        db.session.add(user)
        db.session.flush()

        # 创建学习偏好默认记录
        prefs = LearningPreference(user_id=user.id)
        db.session.add(prefs)

        # 创建邮箱验证令牌
        token_str = generate_token()
        email_token = EmailToken(
            user_id=user.id,
            token=token_str,
            token_type='email_verify',
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        db.session.add(email_token)
        db.session.commit()

        if current_app.config.get('MAIL_SUPPRESS_SEND'):
            # 开发模式：自动激活并打印验证链接到控制台
            user.is_active = True
            db.session.commit()
            verify_url = url_for('auth.verify_email', token=token_str, _external=True)
            current_app.logger.info(f'=' * 50)
            current_app.logger.info(f'开发模式 - 邮箱验证链接: {verify_url}')
            current_app.logger.info(f'用户 {username} 已自动激活，可直接登录。')
            current_app.logger.info(f'=' * 50)
            flash('注册成功！（开发模式：账户已自动激活，可直接登录）', 'success')
        else:
            send_verification_email(user, token_str)
            flash('注册成功！验证邮件已发送到您的邮箱，请查收后激活账户。', 'success')

        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


# ============================================================
# 邮箱验证
# ============================================================

@auth_bp.route('/verify/<token>')
def verify_email(token):
    email_token = EmailToken.query.filter_by(token=token, token_type='email_verify').first()

    if not email_token:
        flash('验证链接无效。', 'danger')
        return redirect(url_for('auth.login'))

    if email_token.is_used:
        flash('该验证链接已被使用。', 'warning')
        return redirect(url_for('auth.login'))

    if email_token.is_expired:
        flash('验证链接已过期，请重新注册。', 'danger')
        return redirect(url_for('auth.register'))

    email_token.is_used = True
    user = User.query.get(email_token.user_id)
    if user:
        user.is_active = True
    db.session.commit()

    flash('邮箱验证成功！请登录。', 'success')
    return redirect(url_for('auth.login'))


# ============================================================
# 登录
# ============================================================

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash('邮箱或密码错误。', 'danger')
            return render_template('auth/login.html', email=email)

        if not user.is_active:
            flash('您的账户尚未激活，请先验证邮箱。', 'warning')
            return render_template('auth/login.html', email=email)

        login_user(user, remember=remember)
        next_page = request.args.get('next')
        if next_page and _is_safe_url(next_page):
            return redirect(next_page)
        return redirect(url_for('main.index'))

    return render_template('auth/login.html')


# ============================================================
# 登出
# ============================================================

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已成功退出登录。', 'info')
    return redirect(url_for('main.index'))


# ============================================================
# 忘记密码
# ============================================================

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user = User.query.filter_by(email=email).first()

        if not user:
            flash('如果该邮箱已注册，您将收到密码重置邮件。', 'info')
            return redirect(url_for('auth.login'))

        token_str = generate_token()
        email_token = EmailToken(
            user_id=user.id,
            token=token_str,
            token_type='password_reset',
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
        db.session.add(email_token)
        db.session.commit()

        if current_app.config.get('MAIL_SUPPRESS_SEND'):
            reset_url = url_for('auth.reset_password', token=token_str, _external=True)
            current_app.logger.info(f'开发模式 - 密码重置链接: {reset_url}')
            flash(f'开发模式：密码重置链接已打印到控制台。', 'success')
        else:
            send_password_reset_email(user, token_str)
            flash('密码重置邮件已发送，请查收。', 'success')

        return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html')


# ============================================================
# 重置密码
# ============================================================

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    email_token = EmailToken.query.filter_by(token=token, token_type='password_reset').first()

    if not email_token or email_token.is_used:
        flash('重置链接无效。', 'danger')
        return redirect(url_for('auth.forgot_password'))

    if email_token.is_expired:
        flash('重置链接已过期，请重新申请。', 'danger')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        if len(password) < 6:
            flash('密码长度至少 6 位。', 'danger')
            return render_template('auth/reset_password.html', token=token)

        if password != confirm:
            flash('两次输入的密码不一致。', 'danger')
            return render_template('auth/reset_password.html', token=token)

        user = User.query.get(email_token.user_id)
        user.set_password(password)
        email_token.is_used = True
        db.session.commit()

        flash('密码重置成功！请使用新密码登录。', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', token=token)
