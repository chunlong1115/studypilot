"""复习提醒蓝图."""
from datetime import datetime
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from studypilot.extensions import db
from studypilot.models import ReviewReminder, ErrorItem, LearningPreference

review_bp = Blueprint('review', __name__, url_prefix='/review')


@review_bp.route('/')
@login_required
def reminders_list():
    # 自动生成提醒
    _generate_reminders()

    reminders = ReviewReminder.query.filter_by(user_id=current_user.id).order_by(
        ReviewReminder.is_read.asc(), ReviewReminder.created_at.desc()
    ).limit(30).all()

    unread_count = ReviewReminder.query.filter_by(user_id=current_user.id, is_read=False).count()

    return render_template('review/reminders.html', reminders=reminders, unread_count=unread_count)


@review_bp.route('/<int:reminder_id>/read', methods=['POST'])
@login_required
def mark_read(reminder_id):
    reminder = ReviewReminder.query.filter_by(id=reminder_id, user_id=current_user.id).first_or_404()
    reminder.is_read = True
    db.session.commit()
    return '', 204


def _generate_reminders():
    """自动生成站内提醒."""
    now = datetime.utcnow()

    # 检查待复习错题
    due_errors = ErrorItem.query.filter_by(user_id=current_user.id, is_resolved=False).filter(
        ErrorItem.next_review_at <= now
    ).count()

    if due_errors > 0:
        existing = ReviewReminder.query.filter_by(
            user_id=current_user.id,
            reminder_type='error_review',
            is_read=False,
        ).first()
        if not existing:
            reminder = ReviewReminder(
                user_id=current_user.id,
                message=f'您有 {due_errors} 道错题待复习，建议尽快回顾巩固。',
                reminder_type='error_review',
            )
            db.session.add(reminder)
            db.session.commit()
