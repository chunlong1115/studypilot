"""错题本蓝图."""
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from studypilot.extensions import db
from studypilot.models import ErrorItem, LearningSession

errors_bp = Blueprint('errors', __name__, url_prefix='/errors')


@errors_bp.route('/')
@login_required
def notebook():
    page = request.args.get('page', 1, type=int)
    show_resolved = request.args.get('resolved') == '1'

    query = ErrorItem.query.filter_by(user_id=current_user.id)

    if not show_resolved:
        query = query.filter_by(is_resolved=False)

    query = query.order_by(ErrorItem.next_review_at.asc())
    pagination = query.paginate(page=page, per_page=15, error_out=False)
    errors = pagination.items

    return render_template('errors/notebook.html',
                           errors=errors,
                           pagination=pagination,
                           show_resolved=show_resolved,
                           now=datetime.utcnow())


@errors_bp.route('/review')
@login_required
def review_mode():
    """间隔重复复习模式：显示最需要复习的题目."""
    items = ErrorItem.query.filter_by(
        user_id=current_user.id, is_resolved=False
    ).filter(
        ErrorItem.next_review_at <= datetime.utcnow()
    ).order_by(ErrorItem.mastery_level.asc()).limit(10).all()

    if not items:
        flash('当前没有需要复习的错题，太棒了！', 'success')
        return redirect(url_for('errors.notebook'))

    return render_template('errors/review.html', items=items)


@errors_bp.route('/<int:error_id>/review', methods=['POST'])
@login_required
def submit_review(error_id):
    """提交复习自评."""
    error = ErrorItem.query.filter_by(id=error_id, user_id=current_user.id).first_or_404()
    rating = request.form.get('rating', 'unsure')

    error.schedule_next_review(rating)
    db.session.commit()

    # 记录学习活动
    session = LearningSession(
        user_id=current_user.id,
        activity_type='review_error',
        duration_minutes=3,
        notes=f'复习错题 #{error.question_id} - {rating}',
    )
    db.session.add(session)
    db.session.commit()

    return redirect(url_for('errors.review_mode'))


@errors_bp.route('/<int:error_id>/resolve', methods=['POST'])
@login_required
def resolve_error(error_id):
    """手动标记错题为已解决."""
    error = ErrorItem.query.filter_by(id=error_id, user_id=current_user.id).first_or_404()
    error.is_resolved = True
    db.session.commit()
    flash('该错题已标记为已掌握。', 'info')
    return redirect(url_for('errors.notebook'))
