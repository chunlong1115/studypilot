from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail

db = SQLAlchemy()  # ORM 数据库操作
migrate = Migrate()  # 数据库迁移工具
login_manager = LoginManager()  # 用户会话管理
mail = Mail()  # 邮件发送

def init_extensions(app):
    """集中初始化所有Flask扩展
    
    Args:
        app: Flask应用实例
    """
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    
    # 配置登录管理器
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录后再访问此页面。'
    login_manager.login_message_category = 'warning'
    
    # 配置会话保护
    login_manager.session_protection = 'strong'
