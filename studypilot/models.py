from datetime import datetime, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from studypilot.extensions import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ============================================================
# 用户与认证
# ============================================================

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    avatar = db.Column(db.String(256), nullable=True)
    is_active = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    preferences = db.relationship('LearningPreference', backref='user', uselist=False,
                                  cascade='all, delete-orphan')
    materials = db.relationship('Material', backref='owner', lazy='dynamic',
                                cascade='all, delete-orphan')
    answers = db.relationship('UserAnswer', backref='user', lazy='dynamic',
                              cascade='all, delete-orphan')
    error_items = db.relationship('ErrorItem', backref='user', lazy='dynamic',
                                  cascade='all, delete-orphan')
    reminders = db.relationship('ReviewReminder', backref='user', lazy='dynamic',
                                cascade='all, delete-orphan')
    sessions = db.relationship('LearningSession', backref='user', lazy='dynamic',
                               cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class EmailToken(db.Model):
    __tablename__ = 'email_tokens'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(128), unique=True, nullable=False, index=True)
    token_type = db.Column(db.String(32), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)

    user = db.relationship('User', backref='email_tokens')

    @property
    def is_expired(self):
        return datetime.utcnow() > self.expires_at


# ============================================================
# 学习偏好
# ============================================================

class LearningPreference(db.Model):
    __tablename__ = 'learning_preferences'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    subject = db.Column(db.String(128), nullable=True)
    learning_goal = db.Column(db.String(256), nullable=True)
    difficulty_level = db.Column(db.String(32), nullable=True, default='beginner')
    daily_study_minutes = db.Column(db.Integer, default=60)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)


# ============================================================
# 学习资料
# ============================================================

class Material(db.Model):
    __tablename__ = 'materials'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(256), nullable=False)
    material_type = db.Column(db.String(32), nullable=False)
    file_path = db.Column(db.String(512), nullable=True)
    content = db.Column(db.Text, nullable=True)
    url = db.Column(db.String(1024), nullable=True)
    file_size = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    summary = db.relationship('AISummary', backref='material', uselist=False,
                              cascade='all, delete-orphan')
    questions = db.relationship('Question', backref='material', lazy='dynamic',
                                cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Material {self.title} ({self.material_type})>'


class AISummary(db.Model):
    __tablename__ = 'ai_summaries'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), unique=True, nullable=False)
    summary_text = db.Column(db.Text, nullable=False)
    key_points = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ============================================================
# 题目与答题
# ============================================================

class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False, index=True)
    question_type = db.Column(db.String(32), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text, nullable=True)
    correct_answer = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text, nullable=True)
    difficulty = db.Column(db.String(16), default='medium')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    answers = db.relationship('UserAnswer', backref='question', lazy='dynamic')

    def __repr__(self):
        return f'<Question {self.id} ({self.question_type})>'


class UserAnswer(db.Model):
    __tablename__ = 'user_answers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False, index=True)
    user_answer = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    answered_at = db.Column(db.DateTime, default=datetime.utcnow)


# ============================================================
# 错题本
# ============================================================

class ErrorItem(db.Model):
    __tablename__ = 'error_items'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    user_answer_id = db.Column(db.Integer, db.ForeignKey('user_answers.id'), nullable=False)
    review_count = db.Column(db.Integer, default=0)
    last_reviewed_at = db.Column(db.DateTime, nullable=True)
    next_review_at = db.Column(db.DateTime, nullable=True)
    mastery_level = db.Column(db.Integer, default=0)
    is_resolved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    question = db.relationship('Question', backref='error_items')
    user_answer = db.relationship('UserAnswer', backref='error_item')

    def get_review_interval(self):
        """简易间隔重复: 根据 mastery_level 返回天数间隔."""
        intervals = [1, 2, 4, 7, 14, 30]
        level = min(self.mastery_level, 5)
        return intervals[level]

    def schedule_next_review(self, rating):
        """根据自评更新掌握度并安排下次复习."""
        if rating == 'mastered':
            self.mastery_level = min(self.mastery_level + 1, 5)
        elif rating == 'unsure':
            self.mastery_level = max(self.mastery_level, 1)
        else:
            self.mastery_level = max(self.mastery_level - 1, 0)

        if self.mastery_level >= 4:
            self.is_resolved = True
            self.next_review_at = None
        else:
            self.next_review_at = datetime.utcnow() + timedelta(days=self.get_review_interval())

        self.review_count += 1
        self.last_reviewed_at = datetime.utcnow()


# ============================================================
# 提醒与学习记录
# ============================================================

class ReviewReminder(db.Model):
    __tablename__ = 'review_reminders'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    message = db.Column(db.String(512), nullable=False)
    reminder_type = db.Column(db.String(32), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class LearningSession(db.Model):
    __tablename__ = 'learning_sessions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    activity_type = db.Column(db.String(64), nullable=False)
    duration_minutes = db.Column(db.Integer, default=0)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=True)
    notes = db.Column(db.String(256), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
