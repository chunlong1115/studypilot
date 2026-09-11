from flask import Flask
from config import DevelopmentConfig


def create_app(config_class=DevelopmentConfig):#应用创建函数，接收配置类参数
    app = Flask(__name__)#创建 Flask 实例
    app.config.from_object(config_class)#从配置类加载配置

    from studypilot.extensions import db, migrate, login_manager, mail # 导入扩展实例
    db.init_app(app)#初始化数据库
    migrate.init_app(app, db)#初始化数据库迁移扩展
    login_manager.init_app(app)#初始化登录管理器
    mail.init_app(app)#初始化邮件扩展

    login_manager.login_view = 'auth.login'#设置未登录用户访问主页时跳转的页面
    login_manager.login_message = '请先登录后再访问此页面。'#设置提示信息

    # 必须在初始化 login_manager 之后导入 models, 确保 user_loader 已注册
    from studypilot import models  # noqa: F401
    # 注册蓝图（Blueprints）- 模块化路由
    from studypilot.blueprints.main import main_bp#导入主页蓝图
    app.register_blueprint(main_bp)#注册主页蓝图

    from studypilot.blueprints.auth import auth_bp#导入用户蓝图
    app.register_blueprint(auth_bp, url_prefix='/auth')#注册用户蓝图

    from studypilot.blueprints.user import user_bp#导入资料蓝图
    app.register_blueprint(user_bp, url_prefix='/user')#注册资料蓝图

    from studypilot.blueprints.materials import materials_bp#导入资料蓝图
    app.register_blueprint(materials_bp)#注册资料蓝图

    from studypilot.blueprints.ai import ai_bp#导入 AI 蓝图
    app.register_blueprint(ai_bp)#注册 AI 蓝图

    from studypilot.blueprints.quiz import quiz_bp#导入测验蓝图
    app.register_blueprint(quiz_bp)#注册测验蓝图

    from studypilot.blueprints.errors import errors_bp#导入错题蓝图
    app.register_blueprint(errors_bp)#注册错题蓝图

    from studypilot.blueprints.progress import progress_bp#导入进度蓝图
    app.register_blueprint(progress_bp)#注册进度蓝图

    from studypilot.blueprints.review import review_bp#导入复习蓝图
    app.register_blueprint(review_bp)#注册复习蓝图

    # HTTP 错误处理
    from flask import render_template#导入模板渲染函数

    @app.errorhandler(404)#404 错误处理
    def not_found(e):#定义404处理函数
        return render_template('errors/404.html'), 404#返回404页面

    @app.errorhandler(500)#注册500错误处理
    def server_error(e):#定义500处理函数
        return render_template('errors/500.html'), 500

    return app
