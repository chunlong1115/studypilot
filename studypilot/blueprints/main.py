from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from studypilot.extensions import db
from studypilot.models import Material, Question, ErrorItem, LearningSession

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    # 统计数据
    material_count = Material.query.filter_by(user_id=current_user.id).count()

    # 题目数 (通过 material 关联)
    question_count = Question.query.join(Material).filter(
        Material.user_id == current_user.id
    ).count()

    # 待复习错题
    pending_errors = ErrorItem.query.filter_by(
        user_id=current_user.id, is_resolved=False
    ).count()

    # 今日学习时间
    today = datetime.utcnow().date()
    today_sessions = LearningSession.query.filter_by(user_id=current_user.id).filter(
        LearningSession.created_at >= today.strftime('%Y-%m-%d')
    ).all()
    today_minutes = sum(s.duration_minutes for s in today_sessions)

    # 总学习天数
    total_sessions = LearningSession.query.filter_by(user_id=current_user.id).count()

    # 最近的错题 (取5条)
    recent_errors = ErrorItem.query.filter_by(
        user_id=current_user.id, is_resolved=False
    ).order_by(ErrorItem.next_review_at.asc()).limit(5).all()

    return render_template('dashboard.html',
                           material_count=material_count,
                           question_count=question_count,
                           pending_errors=pending_errors,
                           today_minutes=today_minutes,
                           total_sessions=total_sessions,
                           recent_errors=recent_errors)


@main_bp.route('/api/study-time', methods=['POST'])
@login_required
def save_study_time():
    """接收前端计时器保存的学习时间."""
    data = request.get_json()
    minutes = max(1, int(data.get('minutes', 1)))
    session = LearningSession(
        user_id=current_user.id,
        activity_type='study_material',
        duration_minutes=minutes,
        notes='前端计时器记录',
    )
    db.session.add(session)
    db.session.commit()
    return jsonify({'success': True, 'minutes': minutes})
