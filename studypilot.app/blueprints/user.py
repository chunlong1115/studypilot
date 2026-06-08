import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from studypilot.extensions import db
from studypilot.models import User, LearningPreference
from studypilot.utils import allowed_file, save_upload

user_bp = Blueprint('user', __name__)


# ============================================================
# 个人信息
# ============================================================

@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()

        errors = []
        if not username or len(username) < 2 or len(username) > 64:
            errors.append('用户名长度应为 2-64 个字符')
        if username != current_user.username and User.query.filter_by(username=username).first():
            errors.append('该用户名已被占用')

        # 头像上传
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file.filename and allowed_file(file.filename, {'png', 'jpg', 'jpeg', 'gif'}):
                old_avatar = current_user.avatar
                avatar_path = save_upload(file, 'avatars')
                current_user.avatar = avatar_path
                # 删除旧头像
                if old_avatar:
                    old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], old_avatar)
                    if os.path.exists(old_path):
                        os.remove(old_path)

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('user/profile.html')

        current_user.username = username
        db.session.commit()
        flash('个人信息已更新。', 'success')
        return redirect(url_for('user.profile'))

    return render_template('user/profile.html')


# ============================================================
# 学习偏好
# ============================================================

@user_bp.route('/preferences', methods=['GET', 'POST'])
@login_required
def preferences():
    prefs = LearningPreference.query.filter_by(user_id=current_user.id).first()
    if not prefs:
        prefs = LearningPreference(user_id=current_user.id)
        db.session.add(prefs)
        db.session.commit()

    if request.method == 'POST':
        prefs.subject = request.form.get('subject', '').strip()
        prefs.learning_goal = request.form.get('learning_goal', '').strip()
        prefs.difficulty_level = request.form.get('difficulty_level', 'beginner')
        daily = request.form.get('daily_study_minutes', '60')
        try:
            prefs.daily_study_minutes = max(10, min(int(daily), 480))
        except (ValueError, TypeError):
            prefs.daily_study_minutes = 60

        db.session.commit()
        flash('学习偏好已保存。', 'success')
        return redirect(url_for('user.preferences'))

    return render_template('user/preferences.html', prefs=prefs)
