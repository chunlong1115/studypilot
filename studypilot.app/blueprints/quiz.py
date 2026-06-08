"""答题蓝图 - 答题 / 提交 / 结果."""
import json
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from studypilot.extensions import db
from studypilot.models import Material, Question, UserAnswer, ErrorItem, LearningSession

quiz_bp = Blueprint('quiz', __name__, url_prefix='/quiz')


@quiz_bp.route('/<int:material_id>/take')
@login_required
def take_quiz(material_id):
    material = Material.query.filter_by(id=material_id, user_id=current_user.id).first_or_404()
    questions = Question.query.filter_by(material_id=material.id).all()

    if not questions:
        flash('该资料还没有题目，请先生成题目。', 'warning')
        return redirect(url_for('ai.generate_quiz_page', material_id=material.id))

    # 解析 options JSON
    for q in questions:
        if q.options:
            try:
                q.parsed_options = json.loads(q.options)
            except (json.JSONDecodeError, TypeError):
                q.parsed_options = []

    return render_template('quiz/take.html', material=material, questions=questions)


@quiz_bp.route('/<int:material_id>/submit', methods=['POST'])
@login_required
def submit_quiz(material_id):
    material = Material.query.filter_by(id=material_id, user_id=current_user.id).first_or_404()
    questions = Question.query.filter_by(material_id=material.id).all()

    if not questions:
        return redirect(url_for('materials.view_material', material_id=material.id))

    total = len(questions)
    correct = 0
    results = []

    # 第一遍：保存所有答题记录
    answer_records = []
    for q in questions:
        user_answer = request.form.get(f'answer_{q.id}', '').strip()
        is_correct = _check_answer(user_answer, q.correct_answer, q.question_type)
        if is_correct:
            correct += 1

        answer_record = UserAnswer(
            user_id=current_user.id,
            question_id=q.id,
            user_answer=user_answer,
            is_correct=is_correct,
        )
        db.session.add(answer_record)
        answer_records.append(answer_record)
        results.append({
            'question': q,
            'user_answer': user_answer,
            'is_correct': is_correct,
        })

    db.session.flush()  # 获取 answer_record.id

    # 第二遍：错题入库
    for i, q in enumerate(questions):
        if not results[i]['is_correct']:
            existing_error = ErrorItem.query.filter_by(
                user_id=current_user.id, question_id=q.id, is_resolved=False
            ).first()
            if not existing_error:
                from datetime import timedelta
                error_item = ErrorItem(
                    user_id=current_user.id,
                    question_id=q.id,
                    user_answer_id=answer_records[i].id,
                    next_review_at=datetime.utcnow() + timedelta(days=1),
                )
                db.session.add(error_item)

    # 记录学习时长(简化为5分钟/题)
    session = LearningSession(
        user_id=current_user.id,
        activity_type='take_quiz',
        duration_minutes=total * 3,
        material_id=material.id,
        notes=f'答题 {total} 题, 正确 {correct} 题',
    )
    db.session.add(session)
    db.session.commit()

    score = round(correct / total * 100) if total > 0 else 0
    return render_template('quiz/result.html', material=material, results=results,
                           total=total, correct=correct, score=score)


def _check_answer(user_answer, correct_answer, question_type):
    """检查答案是否正确."""
    ua = user_answer.strip().lower()
    ca = correct_answer.strip().lower()

    if question_type == 'choice':
        # 比较选项字母 (A/B/C/D)
        return ua == ca or ua == ca.rstrip('.').rstrip(' ')
    elif question_type == 'true_false':
        return ua == ca or (ua in ('对', '正确') and ca in ('正确', '对', 'true')) or (ua in ('错', '错误') and ca in ('错误', '错', 'false'))
    else:
        # 填空和简答：包含匹配
        return ua and (ua == ca or ca in ua or ua in ca)
