from flask import Flask
from config import DevelopmentConfig


def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    from studypilot.extensions import db, migrate, login_manager, mail
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录后再访问此页面。'

    # 必须在初始化 login_manager 之后导入 models, 确保 user_loader 已注册
    from studypilot import models  # noqa: F401

    from studypilot.blueprints.main import main_bp
    app.register_blueprint(main_bp)

    from studypilot.blueprints.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from studypilot.blueprints.user import user_bp
    app.register_blueprint(user_bp, url_prefix='/user')

    from studypilot.blueprints.materials import materials_bp
    app.register_blueprint(materials_bp)

    from studypilot.blueprints.ai import ai_bp
    app.register_blueprint(ai_bp)

    from studypilot.blueprints.quiz import quiz_bp
    app.register_blueprint(quiz_bp)

    from studypilot.blueprints.errors import errors_bp
    app.register_blueprint(errors_bp)

    from studypilot.blueprints.progress import progress_bp
    app.register_blueprint(progress_bp)

    from studypilot.blueprints.review import review_bp
    app.register_blueprint(review_bp)

    # HTTP 错误处理
    from flask import render_template

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    return app
