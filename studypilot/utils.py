import os
import uuid
import secrets
from datetime import datetime, timedelta

from flask import current_app, url_for
from flask_mail import Message
from studypilot.extensions import mail


def allowed_file(filename, allowed_extensions=None):
    if allowed_extensions is None:
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'txt'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def save_upload(file, subfolder=''):
    """保存上传文件，返回相对路径."""
    upload_folder = current_app.config['UPLOAD_FOLDER']
    if subfolder:
        upload_folder = os.path.join(upload_folder, subfolder)
    os.makedirs(upload_folder, exist_ok=True)

    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(upload_folder, unique_name)
    file.save(filepath)

    # 统一用正斜杠（避免 Windows 反斜杠导致 URL 问题）
    return (subfolder + '/' + unique_name) if subfolder else unique_name


def generate_token(length=64):
    """生成随机令牌."""
    return secrets.token_urlsafe(length)


def send_email(to, subject, body):
    """发送邮件."""
    try:
        msg = Message(subject, recipients=[to], body=body)
        mail.send(msg)
        return True
    except Exception:
        current_app.logger.error(f"邮件发送失败: {to}")
        return False


def send_verification_email(user, token):
    """发送邮箱验证邮件."""
    verify_url = url_for('auth.verify_email', token=token, _external=True)
    subject = '智学伴 StudyPilot - 请验证您的邮箱'
    body = f"""您好 {user.username}，

感谢注册智学伴 StudyPilot！

请点击以下链接验证您的邮箱：
{verify_url}

此链接将在 24 小时后失效。

智学伴 StudyPilot 团队
"""
    return send_email(user.email, subject, body)


def send_password_reset_email(user, token):
    """发送密码重置邮件."""
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    subject = '智学伴 StudyPilot - 密码重置'
    body = f"""您好 {user.username}，

请点击以下链接重置您的密码：
{reset_url}

此链接将在 1 小时后失效。

如果您没有请求重置密码，请忽略此邮件。

智学伴 StudyPilot 团队
"""
    return send_email(user.email, subject, body)
