"""AI 功能蓝图 - 摘要生成 & 题目生成."""
import json
from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from studypilot.extensions import db
from studypilot.models import Material, AISummary, Question, LearningPreference
from studypilot.services.ai_service import generate_summary, generate_quiz

ai_bp = Blueprint('ai', __name__, url_prefix='/ai')


def _get_user_prefs():
    prefs = LearningPreference.query.filter_by(user_id=current_user.id).first()
    if prefs:
        return {
            'subject': prefs.subject,
            'learning_goal': prefs.learning_goal,
            'difficulty_level': prefs.difficulty_level or 'beginner',
            'daily_study_minutes': prefs.daily_study_minutes or 60,
        }
    return {}


# ============================================================
# 生成摘要 (AJAX)
# ============================================================

@ai_bp.route('/generate-summary/<int:material_id>', methods=['POST'])
@login_required
def generate_summary_api(material_id):
    material = Material.query.filter_by(id=material_id, user_id=current_user.id).first_or_404()

    if not material.content or len(material.content.strip()) < 20:
        return jsonify({'success': False, 'message': '该资料无可提取的文本内容。'}), 400

    prefs = _get_user_prefs()
    try:
        summary_text, key_points = generate_summary(material.content, prefs)
    except Exception:
        return jsonify({'success': False, 'message': 'AI 服务调用失败，请检查 API Key 配置。'}), 500

    existing = AISummary.query.filter_by(material_id=material.id).first()
    if existing:
        db.session.delete(existing)
        db.session.flush()

    ai_summary = AISummary(
        material_id=material.id,
        summary_text=summary_text,
        key_points=key_points,
    )
    db.session.add(ai_summary)
    db.session.commit()

    return jsonify({'success': True, 'summary': summary_text, 'key_points': key_points})


# ============================================================
# 生成题目
# ============================================================

@ai_bp.route('/generate-quiz/<int:material_id>', methods=['GET', 'POST'])
@login_required
def generate_quiz_page(material_id):
    material = Material.query.filter_by(id=material_id, user_id=current_user.id).first_or_404()

    if not material.content or len(material.content.strip()) < 50:
        flash('该资料内容太短，无法生成题目。', 'danger')
        return redirect(url_for('materials.view_material', material_id=material.id))

    if request.method == 'POST':
        count = int(request.form.get('count', 5))
        types = request.form.getlist('types') or ['choice', 'fill_blank', 'true_false', 'short_answer']
        difficulty = request.form.get('difficulty', 'medium')

        prefs = _get_user_prefs()
        try:
            questions_data = generate_quiz(material.content, count=count, question_types=types,
                                           difficulty=difficulty, user_prefs=prefs)
        except ValueError as e:
            flash(str(e), 'danger')
            return render_template('quiz/generate.html', material=material)
        except Exception:
            flash('AI 服务调用失败，请检查 API Key 配置。', 'danger')
            return render_template('quiz/generate.html', material=material)

        # 清除旧题目（先删关联数据，避免外键冲突）
        old_questions = Question.query.filter_by(material_id=material.id).all()
        for old_q in old_questions:
            from studypilot.models import UserAnswer, ErrorItem
            ErrorItem.query.filter_by(question_id=old_q.id).delete()
            UserAnswer.query.filter_by(question_id=old_q.id).delete()
        db.session.flush()
        Question.query.filter_by(material_id=material.id).delete()
        for q_data in questions_data:
            question = Question(
                material_id=material.id,
                question_type=q_data.get('type', 'choice'),
                question_text=q_data.get('question', ''),
                options=json.dumps(q_data.get('options', []), ensure_ascii=False) if q_data.get('options') else None,
                correct_answer=q_data.get('answer', ''),
                explanation=q_data.get('explanation', ''),
                difficulty=q_data.get('difficulty', 'medium'),
            )
            db.session.add(question)
        db.session.commit()

        return redirect(url_for('quiz.take_quiz', material_id=material.id))

    return render_template('quiz/generate.html', material=material)
