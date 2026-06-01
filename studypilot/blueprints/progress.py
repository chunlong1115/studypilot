"""学习进度蓝图."""
from datetime import datetime, timedelta
from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from studypilot.models import Material, Question, ErrorItem, LearningSession

progress_bp = Blueprint('progress', __name__, url_prefix='/progress')


@progress_bp.route('/')
@login_required
def dashboard():
    # 总计学习时间
    sessions = LearningSession.query.filter_by(user_id=current_user.id).all()
    total_minutes = sum(s.duration_minutes for s in sessions)
    total_hours = round(total_minutes / 60, 1)

    # 答题统计
    material_count = Material.query.filter_by(user_id=current_user.id).count()
    question_count = Question.query.join(Material).filter(Material.user_id == current_user.id).count()

    # 错题解决率
    total_errors = ErrorItem.query.filter_by(user_id=current_user.id).count()
    resolved_errors = ErrorItem.query.filter_by(user_id=current_user.id, is_resolved=True).count()
    resolve_rate = round(resolved_errors / total_errors * 100) if total_errors > 0 else 0

    # 近7天学习数据
    daily_data = []
    for i in range(6, -1, -1):
        day = datetime.utcnow() - timedelta(days=i)
        day_start = day.strftime('%Y-%m-%d')
        day_end = (day + timedelta(days=1)).strftime('%Y-%m-%d')
        day_sessions = LearningSession.query.filter_by(user_id=current_user.id).filter(
            LearningSession.created_at >= day_start,
            LearningSession.created_at < day_end,
        ).all()
        day_minutes = sum(s.duration_minutes for s in day_sessions)
        daily_data.append({
            'date': day.strftime('%m-%d'),
            'minutes': day_minutes,
        })

    return render_template('progress/dashboard.html',
                           total_hours=total_hours,
                           material_count=material_count,
                           question_count=question_count,
                           total_errors=total_errors,
                           resolved_errors=resolved_errors,
                           resolve_rate=resolve_rate,
                           daily_data=daily_data)


@progress_bp.route('/api/stats')
@login_required
def api_stats():
    """返回 JSON 统计数据供 Chart.js 使用."""
    daily_data = []
    for i in range(6, -1, -1):
        day = datetime.utcnow() - timedelta(days=i)
        day_start = day.strftime('%Y-%m-%d')
        day_end = (day + timedelta(days=1)).strftime('%Y-%m-%d')
        day_sessions = LearningSession.query.filter_by(user_id=current_user.id).filter(
            LearningSession.created_at >= day_start,
            LearningSession.created_at < day_end,
        ).all()
        daily_data.append({
            'date': day.strftime('%m-%d'),
            'minutes': sum(s.duration_minutes for s in day_sessions),
        })

    return jsonify({'daily': daily_data})
