# 导入日期时间模块，用于时间戳和间隔计算
from datetime import datetime, timedelta
# 导入 Flask-Login 的用户混入类，提供默认的用户认证方法
from flask_login import UserMixin
# 导入密码哈希工具，用于安全存储和验证密码
from werkzeug.security import generate_password_hash, check_password_hash
# 导入数据库实例和登录管理器
from studypilot.extensions import db, login_manager


# Flask-Login 的用户加载回调函数
# 当用户会话中存在 user_id 时，自动调用此函数加载用户对象
@login_manager.user_loader
def load_user(user_id):
    """根据用户ID从数据库加载用户对象
    
    Args:
        user_id: 会话中存储的用户ID（字符串类型）
    
    Returns:
        User对象或None（用户不存在时）
    """
    # 将字符串ID转换为整数，通过主键查询用户
    return User.query.get(int(user_id))


# ============================================================
# 用户与认证模块
# 包含用户基本信息、邮箱验证令牌等
# ============================================================

class User(UserMixin, db.Model):
    """用户模型 - 存储平台用户的基本信息和认证数据
    
    继承 UserMixin 获得 Flask-Login 所需的默认方法：
    - is_authenticated: 用户是否已认证
    - is_active: 用户账户是否激活
    - is_anonymous: 是否为匿名用户
    - get_id(): 返回用户ID
    """
    # 指定数据库表名为 'users'
    __tablename__ = 'users'

    # 主键ID，自增长整数，唯一标识每个用户
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 用户名，最大64字符，唯一约束，创建索引加速查询，不能为空
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    # 邮箱地址，最大120字符，唯一约束，创建索引，不能为空
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    # 密码哈希值，不存储明文密码，使用 Werkzeug 的 PBKDF2+SHA256 算法
    password_hash = db.Column(db.String(256), nullable=False)
    # 头像文件路径，相对于上传文件夹的路径，允许为空
    avatar = db.Column(db.String(256), nullable=True)
    # 账户激活状态，新用户默认为False，需邮箱验证后激活
    is_active = db.Column(db.Boolean, default=False)
    # 管理员标志，预留字段用于权限控制
    is_admin = db.Column(db.Boolean, default=False)
    # 账户创建时间，默认为当前UTC时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # 最后更新时间，创建和每次更新时自动刷新
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ==================== 关系定义 ====================
    # 与学习偏好的一对一关系
    # uselist=False 表示返回单个对象而非列表
    # cascade='all, delete-orphan' 表示删除用户时同时删除其偏好设置
    preferences = db.relationship('LearningPreference', backref='user', uselist=False,
                                  cascade='all, delete-orphan')
    
    # 与学习资料的一对多关系
    # lazy='dynamic' 返回查询对象，支持进一步过滤和分页
    # backref='owner' 在 Material 模型中添加 owner 属性反向访问用户
    materials = db.relationship('Material', backref='owner', lazy='dynamic',
                                cascade='all, delete-orphan')
    
    # 与答题记录的一对多关系
    answers = db.relationship('UserAnswer', backref='user', lazy='dynamic',
                              cascade='all, delete-orphan')
    
    # 与错题本的一对多关系
    error_items = db.relationship('ErrorItem', backref='user', lazy='dynamic',
                                  cascade='all, delete-orphan')
    
    # 与复习提醒的一对多关系
    reminders = db.relationship('ReviewReminder', backref='user', lazy='dynamic',
                                cascade='all, delete-orphan')
    
    # 与学习记录的一对多关系
    sessions = db.relationship('LearningSession', backref='user', lazy='dynamic',
                               cascade='all, delete-orphan')

    def set_password(self, password):
        """设置用户密码
        
        将明文密码转换为哈希值后存储，确保密码安全。
        使用 PBKDF2 算法 + SHA256 哈希 + 随机盐值。
        
        Args:
            password: 用户输入的明文密码
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """验证用户密码
        
        将输入的明文密码与存储的哈希值进行比对。
        
        Args:
            password: 用户尝试登录时输入的明文密码
            
        Returns:
            bool: 密码正确返回True，错误返回False
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        """定义对象的字符串表示形式，用于调试和日志输出
        
        Returns:
            str: 格式为 '<User 用户名>'
        """
        return f'<User {self.username}>'


class EmailToken(db.Model):
    """邮箱验证令牌模型 - 用于邮箱验证和密码重置
    
    存储临时生成的令牌，具有过期时间和使用状态，
    防止令牌被重复使用或长期有效带来的安全风险。
    """
    __tablename__ = 'email_tokens'

    # 主键ID
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 外键关联用户，一个用户可以有多个令牌（多次注册/重置）
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # 令牌字符串，URL安全的随机字符串，唯一且带索引加速查询
    token = db.Column(db.String(128), unique=True, nullable=False, index=True)
    # 令牌类型：'email_verify'（邮箱验证）或 'password_reset'（密码重置）
    token_type = db.Column(db.String(32), nullable=False)
    # 过期时间，邮箱验证24小时，密码重置1小时
    expires_at = db.Column(db.DateTime, nullable=False)
    # 是否已被使用，防止重放攻击
    is_used = db.Column(db.Boolean, default=False)

    # 与用户的多对一关系
    # backref='email_tokens' 在 User 模型中添加 email_tokens 属性
    user = db.relationship('User', backref='email_tokens')

    @property
    def is_expired(self):
        """检查令牌是否已过期的属性方法
        
        使用 @property 装饰器使其像属性一样调用：token.is_expired
        
        Returns:
            bool: 当前时间超过过期时间返回True
        """
        return datetime.utcnow() > self.expires_at


# ============================================================
# 学习偏好模块
# 存储用户的个性化学习设置，用于AI定制化服务
# ============================================================

class LearningPreference(db.Model):
    """学习偏好模型 - 存储用户的个性化学习配置
    
    每个用户只能有一条偏好记录（一对一关系），
    用于AI生成摘要和题目时参考用户的学科、目标、难度偏好。
    """
    __tablename__ = 'learning_preferences'

    # 主键ID
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 外键关联用户，unique=True 确保一对一关系
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    # 学科方向，如"计算机科学"、"高等数学"，允许为空
    subject = db.Column(db.String(128), nullable=True)
    # 学习目标，如"通过期末考试"、"掌握Python编程"
    learning_goal = db.Column(db.String(256), nullable=True)
    # 难度偏好：'beginner'（初级）、'intermediate'（中级）、'advanced'（高级）
    difficulty_level = db.Column(db.String(32), nullable=True, default='beginner')
    # 每日学习时长目标（分钟），默认60分钟
    daily_study_minutes = db.Column(db.Integer, default=60)
    # 偏好设置的最后更新时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)


# ============================================================
# 学习资料模块
# 管理用户上传的学习材料，包括笔记和图片
# ============================================================

class Material(db.Model):
    """学习资料模型 - 存储用户上传的各种学习资料
    
    支持两种类型：
    - note: 文本笔记，内容存储在 content 字段
    - image: 图片文件，路径存储在 file_path 字段
    
    资料可以被AI分析生成摘要和题目。
    """
    __tablename__ = 'materials'

    # 主键ID
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 外键关联用户，带索引加速按用户查询资料列表
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    # 资料标题，不能为空，最大256字符
    title = db.Column(db.String(256), nullable=False)
    # 资料类型：'note'（笔记）或 'image'（图片）
    material_type = db.Column(db.String(32), nullable=False)
    # 文件存储路径，仅图片类型使用，相对于UPLOAD_FOLDER的路径
    file_path = db.Column(db.String(512), nullable=True)
    # 文本内容，仅笔记类型使用，Text类型无长度限制
    content = db.Column(db.Text, nullable=True)
    # 网页链接，预留字段，当前版本可能未使用
    url = db.Column(db.String(1024), nullable=True)
    # 文件大小（字节），仅图片类型使用
    file_size = db.Column(db.Integer, nullable=True)
    # 创建时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # 更新时间，修改资料时自动刷新
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 与AI摘要的一对一关系
    # 一个资料最多有一个AI生成的摘要
    summary = db.relationship('AISummary', backref='material', uselist=False,
                              cascade='all, delete-orphan')
    
    # 与题目的一对多关系
    # 一个资料可以生成多道练习题
    questions = db.relationship('Question', backref='material', lazy='dynamic',
                                cascade='all, delete-orphan')

    def __repr__(self):
        """定义资料的字符串表示，用于调试
        
        Returns:
            str: 格式为 '<Material 标题 (类型)>'
        """
        return f'<Material {self.title} ({self.material_type})>'


class AISummary(db.Model):
    """AI摘要模型 - 存储DeepSeek生成的学习资料摘要
    
    每个资料对应一个摘要，包含内容摘要和关键知识点提取。
    重新生成时会删除旧摘要并创建新记录。
    """
    __tablename__ = 'ai_summaries'

    # 主键ID
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 外键关联资料，unique=True 确保一对一关系
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), unique=True, nullable=False)
    # AI生成的摘要文本，200字以内的内容概括
    summary_text = db.Column(db.Text, nullable=False)
    # 关键知识点列表，格式为 "1. 知识点一\n2. 知识点二"
    key_points = db.Column(db.Text, nullable=True)
    # 摘要生成时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ============================================================
# 题目与答题模块
# 管理AI生成的练习题和用户的答题记录
# ============================================================

class Question(db.Model):
    """题目模型 - 存储AI生成的练习题
    
    支持四种题型：
    - choice: 选择题，需提供options选项数组
    - fill_blank: 填空题
    - true_false: 判断题
    - short_answer: 简答题
    
    题目基于学习资料内容生成，包含答案和解析。
    """
    __tablename__ = 'questions'

    # 主键ID
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 外键关联资料，带索引加速按资料查询题目
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False, index=True)
    # 题型标识
    question_type = db.Column(db.String(32), nullable=False)
    # 题目内容文本
    question_text = db.Column(db.Text, nullable=False)
    # 选项数组（JSON格式），仅选择题使用
    # 示例: '["A. 选项一", "B. 选项二", "C. 选项三", "D. 选项四"]'
    options = db.Column(db.Text, nullable=True)
    # 正确答案，不同题型的格式不同
    correct_answer = db.Column(db.Text, nullable=False)
    # 答案解析，帮助用户理解为什么选这个答案
    explanation = db.Column(db.Text, nullable=True)
    # 难度等级：'easy'、'medium'、'hard'
    difficulty = db.Column(db.String(16), default='medium')
    # 题目创建时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 与答题记录的一对多关系
    # 一道题可以被多个用户回答，或同一用户多次回答
    answers = db.relationship('UserAnswer', backref='question', lazy='dynamic')

    def __repr__(self):
        """定义题目的字符串表示
        
        Returns:
            str: 格式为 '<Question ID (题型)>'
        """
        return f'<Question {self.id} ({self.question_type})>'


class UserAnswer(db.Model):
    """答题记录模型 - 存储用户的每次答题行为
    
    记录用户回答的题目、答案内容、是否正确等信息，
    用于统计分析、错题收录和学习进度追踪。
    """
    __tablename__ = 'user_answers'

    # 主键ID
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 外键关联用户，带索引
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    # 外键关联题目，带索引
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False, index=True)
    # 用户提交的答案内容
    user_answer = db.Column(db.Text, nullable=False)
    # 答案是否正确，用于统计正确率和筛选错题
    is_correct = db.Column(db.Boolean, nullable=False)
    # 答题时间戳
    answered_at = db.Column(db.DateTime, default=datetime.utcnow)


# ============================================================
# 错题本模块
# 核心功能：基于间隔重复算法的智能错题管理
# ============================================================

class ErrorItem(db.Model):
    """错题本模型 - 存储用户答错的题目及复习状态
    
    实现基于艾宾浩斯遗忘曲线的间隔重复算法：
    - 根据掌握程度动态调整复习间隔
    - 用户自评后更新下次复习时间
    - 达到掌握标准后标记为已解决
    
    掌握等级与复习间隔对应关系：
    等级0 → 1天 | 等级1 → 2天 | 等级2 → 4天
    等级3 → 7天 | 等级4 → 14天 | 等级5 → 30天
    """
    __tablename__ = 'error_items'

    # 主键ID
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 外键关联用户，带索引
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    # 外键关联原始题目
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    # 外键关联用户的错误答题记录，保留当时的答案供回顾
    user_answer_id = db.Column(db.Integer, db.ForeignKey('user_answers.id'), nullable=False)
    # 复习次数统计，初始为0
    review_count = db.Column(db.Integer, default=0)
    # 上次复习的时间戳
    last_reviewed_at = db.Column(db.DateTime, nullable=True)
    # 下次复习的时间戳，由算法动态计算
    next_review_at = db.Column(db.DateTime, nullable=True)
    # 掌握程度等级，范围0-5，0为完全不会，5为完全掌握
    mastery_level = db.Column(db.Integer, default=0)
    # 是否已解决，达到掌握标准后设为True，不再出现在待复习列表
    is_resolved = db.Column(db.Boolean, default=False)
    # 错题创建时间（首次答错的时间）
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 与题目的多对一关系
    # 通过 error_item.question 访问原始题目内容
    question = db.relationship('Question', backref='error_items')
    
    # 与答题记录的一对一关系
    # 通过 error_item.user_answer 查看用户的错误答案
    user_answer = db.relationship('UserAnswer', backref='error_item')

    def get_review_interval(self):
        """根据掌握程度获取复习间隔天数
        
        实现简化的SM-2间隔重复算法，基于艾宾浩斯遗忘曲线。
        掌握程度越高，复习间隔越长，符合记忆规律。
        
        Returns:
            int: 距离下次复习的天数间隔
            
        间隔规则：
            等级0 → 1天（刚答错，需尽快复习）
            等级1 → 2天
            等级2 → 4天
            等级3 → 7天
            等级4 → 14天
            等级5 → 30天（已掌握，间隔最长）
        """
        # 定义各等级对应的复习间隔天数数组
        intervals = [1, 2, 4, 7, 14, 30]
        # 限制等级范围在0-5之间，防止数组越界
        level = min(self.mastery_level, 5)
        # 返回对应等级的间隔天数
        return intervals[level]

    def schedule_next_review(self, rating):
        """根据用户自评安排下次复习时间
        
        核心算法流程：
        1. 根据自评调整掌握程度等级
        2. 判断是否达到掌握标准（等级>=4）
        3. 计算下次复习时间或标记为已解决
        4. 更新复习次数和时间戳
        
        Args:
            rating: 用户自评结果
                - 'mastered': 掌握了，提升等级
                - 'unsure': 不确定，保持等级
                - 其他: 没掌握，降低等级
        
        使用示例：
            error.schedule_next_review('mastered')  # 用户自评掌握了
            error.schedule_next_review('unsure')    # 用户不确定
            error.schedule_next_review('failed')    # 用户没掌握
        """
        # 根据自评调整掌握程度等级
        if rating == 'mastered':
            # 用户表示掌握了，等级+1，最高不超过5
            self.mastery_level = min(self.mastery_level + 1, 5)
        elif rating == 'unsure':
            # 用户不确定，保持当前等级或至少设为1
            # max确保不会降到0，表示还有些印象
            self.mastery_level = max(self.mastery_level, 1)
        else:
            # 用户没掌握（rating为其他值），等级-1
            # max确保不会低于0
            self.mastery_level = max(self.mastery_level - 1, 0)

        # 判断是否达到掌握标准
        if self.mastery_level >= 4:
            # 等级达到4或以上，标记为已解决
            self.is_resolved = True
            # 清除下次复习时间，不再安排复习
            self.next_review_at = None
        else:
            # 未达到掌握标准，计算下次复习时间
            # 当前时间 + 根据等级计算的间隔天数
            self.next_review_at = datetime.utcnow() + timedelta(days=self.get_review_interval())

        # 复习次数+1
        self.review_count += 1
        # 更新上次复习时间为当前时间
        self.last_reviewed_at = datetime.utcnow()


# ============================================================
# 提醒与学习记录模块
# 站内消息提醒和学习时长统计
# ============================================================

class ReviewReminder(db.Model):
    """复习提醒模型 - 存储站内消息提醒
    
    系统自动生成的提醒消息，如错题复习提醒、学习目标提醒等。
    支持已读/未读状态管理，未读提醒优先显示。
    """
    __tablename__ = 'review_reminders'

    # 主键ID
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 外键关联用户，带索引
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    # 提醒消息内容，最大512字符
    # 示例："您有5道错题待复习，建议尽快回顾巩固。"
    message = db.Column(db.String(512), nullable=False)
    # 提醒类型，如 'error_review'（错题复习提醒）
    reminder_type = db.Column(db.String(32), nullable=False)
    # 是否已读，未读提醒优先展示
    is_read = db.Column(db.Boolean, default=False)
    # 提醒创建时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class LearningSession(db.Model):
    """学习记录模型 - 存储用户的学习活动会话
    
    记录用户的每次学习活动，包括：
    - 阅读资料
    - 答题练习
    - 复习错题
    
    用于统计学习时长、分析学习趋势、生成进度图表。
    """
    __tablename__ = 'learning_sessions'

    # 主键ID
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 外键关联用户，带索引
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    # 活动类型，区分不同的学习行为
    # 可选值：'study_material'、'take_quiz'、'review_error'
    activity_type = db.Column(db.String(64), nullable=False)
    # 学习时长（分钟）
    # 来源：前端计时器上报 或 根据题目数量估算
    duration_minutes = db.Column(db.Integer, default=0)
    # 外键关联资料（可选），如果学习活动针对特定资料则记录
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=True)
    # 备注信息，记录详细说明
    # 示例："前端计时器记录"、"答题10题, 正确8题"
    notes = db.Column(db.String(256), nullable=True)
    # 学习时间戳，用于按日期统计
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
