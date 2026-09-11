import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production·')

    # MySQL数据库配置
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'mysql+pymysql://root:password@localhost:3306/studypilot?charset=utf8mb4'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False  #禁用SQLAlchemy的事件系统以提高性能

    # Upload文件上传配置
    UPLOAD_FOLDER = os.path.join(basedir, 'studypilot', 'static', 'uploads')#上传文件夹路径
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  #最大上传文件大小16MB

    # 邮件配置（用于注册验证和密码重置）
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.qq.com')#邮件服务器
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))#邮件服务器端口
    MAIL_USE_TLS = True#启用TLS加密
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')#邮件服务器用户名
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')#邮件服务器密码
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@studypilot.com')#发件人

    #DeepSeek AI API配置
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')#DeepSeek API密钥
    DEEPSEEK_BASE_URL = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')#DeepSeek API地址
    DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')#DeepSeek模型

    ITEMS_PER_PAGE = 10 #每页显示的条目数


class DevelopmentConfig(Config):#开发环境配置
    DEBUG = True#开启调试模式
    MAIL_SUPPRESS_SEND = True#开发模式禁用邮件发送
    MAIL_DEBUG = True#邮件调试模式


class ProductionConfig(Config):#测试环境配置
    DEBUG = False#关闭调试模式


class TestingConfig(Config):#测试环境配置
    TESTING = True#开启测试模式
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'#使用内存sqlite数据库