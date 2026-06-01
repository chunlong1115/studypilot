import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from studypilot.extensions import db
from studypilot.models import Material, AISummary
from studypilot.utils import allowed_file, save_upload
from studypilot.services.material_service import extract_pdf_text

materials_bp = Blueprint('materials', __name__, url_prefix='/materials')


# ============================================================
# 资料列表
# ============================================================

@materials_bp.route('/')
@login_required
def list_materials():
    page = request.args.get('page', 1, type=int)
    type_filter = request.args.get('type', '')

    query = Material.query.filter_by(user_id=current_user.id)
    if type_filter in ('pdf', 'note', 'image', 'link'):
        query = query.filter_by(material_type=type_filter)

    query = query.order_by(Material.updated_at.desc())
    per_page = current_app.config.get('ITEMS_PER_PAGE', 10)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    materials = pagination.items

    return render_template('materials/list.html',
                           materials=materials,
                           pagination=pagination,
                           type_filter=type_filter)


# ============================================================
# 上传资料
# ============================================================

@materials_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_material():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        mtype = request.form.get('material_type', '')

        if not title:
            flash('请输入资料标题。', 'danger')
            return render_template('materials/upload.html')

        if mtype not in ('pdf', 'note', 'image', 'link'):
            flash('请选择有效的资料类型。', 'danger')
            return render_template('materials/upload.html')

        material = Material(
            user_id=current_user.id,
            title=title,
            material_type=mtype
        )

        if mtype == 'pdf':
            file = request.files.get('file')
            if not file or not file.filename:
                flash('请选择要上传的 PDF 文件。', 'danger')
                return render_template('materials/upload.html')
            if not allowed_file(file.filename, {'pdf'}):
                flash('仅支持 PDF 格式。', 'danger')
                return render_template('materials/upload.html')
            filepath = save_upload(file, 'materials')
            material.file_path = filepath
            material.file_size = os.path.getsize(
                os.path.join(current_app.config['UPLOAD_FOLDER'], filepath)
            )
            # 提取 PDF 文本
            full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filepath)
            material.content = extract_pdf_text(full_path)
            if not material.content:
                flash('PDF 文件已上传，但未能自动提取文字内容（可能是扫描件或图片型 PDF）。你可以手动补充文本内容。', 'warning')

        elif mtype == 'note':
            material.content = request.form.get('content', '').strip()
            if not material.content:
                flash('请输入笔记内容。', 'danger')
                return render_template('materials/upload.html')

        elif mtype == 'image':
            file = request.files.get('file')
            if not file or not file.filename:
                flash('请选择要上传的图片。', 'danger')
                return render_template('materials/upload.html')
            if not allowed_file(file.filename, {'png', 'jpg', 'jpeg', 'gif'}):
                flash('仅支持 PNG/JPG/JPEG/GIF 格式。', 'danger')
                return render_template('materials/upload.html')
            filepath = save_upload(file, 'materials')
            material.file_path = filepath
            material.file_size = os.path.getsize(
                os.path.join(current_app.config['UPLOAD_FOLDER'], filepath)
            )

        elif mtype == 'link':
            url_input = request.form.get('url', '').strip()
            if not url_input:
                flash('请输入网页链接。', 'danger')
                return render_template('materials/upload.html')
            if not url_input.startswith(('http://', 'https://')):
                url_input = 'https://' + url_input
            material.url = url_input

        db.session.add(material)
        db.session.commit()
        flash(f'资料"{title}"已上传。', 'success')
        return redirect(url_for('materials.view_material', material_id=material.id))

    return render_template('materials/upload.html')


# ============================================================
# 查看资料
# ============================================================

@materials_bp.route('/<int:material_id>')
@login_required
def view_material(material_id):
    material = Material.query.filter_by(id=material_id, user_id=current_user.id).first_or_404()
    summary = AISummary.query.filter_by(material_id=material.id).first()
    return render_template('materials/view.html', material=material, summary=summary)


# ============================================================
# 编辑笔记
# ============================================================

@materials_bp.route('/<int:material_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_material(material_id):
    material = Material.query.filter_by(id=material_id, user_id=current_user.id).first_or_404()
    if material.material_type not in ('note', 'pdf'):
        flash('仅笔记和 PDF 类型资料支持编辑。', 'danger')
        return redirect(url_for('materials.view_material', material_id=material.id))

    if request.method == 'POST':
        material.title = request.form.get('title', '').strip()
        material.content = request.form.get('content', '').strip()
        if not material.title:
            flash('请输入标题。', 'danger')
            return render_template('materials/edit_note.html', material=material)
        db.session.commit()
        flash('笔记已更新。', 'success')
        return redirect(url_for('materials.view_material', material_id=material.id))

    return render_template('materials/edit_note.html', material=material)


# ============================================================
# 删除资料
# ============================================================

@materials_bp.route('/<int:material_id>/delete', methods=['POST'])
@login_required
def delete_material(material_id):
    material = Material.query.filter_by(id=material_id, user_id=current_user.id).first_or_404()

    # 删除对应文件
    if material.file_path:
        full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], material.file_path)
        if os.path.exists(full_path):
            os.remove(full_path)

    # 删除关联摘要
    AISummary.query.filter_by(material_id=material.id).delete()

    db.session.delete(material)
    db.session.commit()
    flash(f'资料"{material.title}"已删除。', 'info')
    return redirect(url_for('materials.list_materials'))
