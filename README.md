# 智学伴 StudyPilot — AI 智能学习辅助平台

>  | Flask + MySQL + DeepSeek AI | 

## 项目简介

智学伴（StudyPilot）是一个面向大学生的 AI 智能学习辅助平台，结合大语言模型实现学习资料的智能管理、自动摘要生成、AI 出题练习、错题管理与间隔重复复习、学习进度可视化分析等功能。

## 技术架构

```
前端 (Bootstrap 5 + Chart.js + 原生 JS)
        ↓
Flask Web 路由层 (9 个 Blueprint 模块)
        ↓
业务逻辑层 (AI Service / Quiz Service / Review Service)
        ↓
DeepSeek API (OpenAI 兼容接口)
        ↓
MySQL 8.0 数据库 + SQLAlchemy ORM
```

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | Python Flask 3.1 |
| 数据库 | MySQL 8.0 + SQLAlchemy 2.0 ORM |
| 迁移工具 | Flask-Migrate / Alembic |
| AI 引擎 | DeepSeek API (openai SDK) |
| 认证 | Flask-Login + 邮箱验证 |
| 前端 | Bootstrap 5 + Chart.js + Bootstrap Icons |
| PDF 处理 | PyMuPDF (fitz) |

## 功能模块

| 模块 | 功能 |
|------|------|
| 用户系统 | 注册/登录、邮箱验证、密码重置、个人中心、学习偏好 |
| 学习资料 | 文本笔记上传、图片上传、资料列表与筛选 |
| AI 摘要 | DeepSeek 自动生成学习摘要与关键知识点 |
| AI 出题 | 选择题/填空题/判断题/简答题四种题型自动生成 |
| 在线答题 | 单选题、判断题、填空题实时作答与即时评分 |
| 错题本 | 答错自动收录、间隔重复算法(SM-2简化版)、复习模式 |
| 学习进度 | Chart.js 可视化图表、学习时长统计、近7天趋势 |
| 智能提醒 | 站内错题复习提醒、每日学习目标提醒 |

## 数据库设计 (10 张表)

```
users                  learning_preferences   email_tokens
materials              ai_summaries           questions
user_answers           error_items            review_reminders
learning_sessions
```

## 快速启动

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 .env (复制 .env.example)
cp .env.example .env
# 编辑 .env 填入 MySQL 密码和 DeepSeek API Key

# 3. 启动应用
python run.py
# 浏览器打开 http://127.0.0.1:5000
```

## 项目结构

```
studypilot/
├── run.py                        # 应用入口
├── config.py                     # 配置类
├── requirements.txt              # 依赖清单
├── studypilot/
│   ├── __init__.py               # App 工厂 + 蓝图注册 + 错误处理
│   ├── models.py                 # 10 张 SQLAlchemy 数据模型
│   ├── extensions.py             # Flask 扩展初始化
│   ├── utils.py                  # 工具函数 (邮件/文件上传/令牌)
│   ├── blueprints/               # 9 个蓝图模块
│   │   ├── auth.py               # 认证 (注册/登录/邮箱验证/密码重置)
│   │   ├── main.py               # 首页 + 仪表盘
│   │   ├── user.py               # 个人中心 + 学习偏好
│   │   ├── materials.py          # 学习资料 CRUD
│   │   ├── ai.py                 # AI 摘要 + AI 出题
│   │   ├── quiz.py               # 答题 + 评分 + 错题入库
│   │   ├── errors.py             # 错题本 + 间隔重复复习
│   │   ├── progress.py           # 学习进度 + Chart.js 图表
│   │   └── review.py             # 站内复习提醒
│   ├── services/                 # 业务逻辑层
│   │   └── ai_service.py         # DeepSeek API 调用 + Prompt 工程
│   ├── static/                   # CSS / JS / 上传文件
│   └── templates/                # Jinja2 模板 (21 个页面)
└── docs/                         # 项目文档
```

## 核心亮点

1. **AI 驱动** — DeepSeek 大模型实现智能摘要和出题
2. **间隔重复** — 基于 SM-2 简化算法的科学错题复习
3. **多题型支持** — 选择题、填空题、判断题、简答题
4. **可视化分析** — Chart.js 实时图表展示学习进度
5. **模块化架构** — Flask Blueprint + Service 分层，清晰可维护
6. **安全设计** — 密码哈希存储、邮箱验证、开放重定向防护

## 作者
椿  
数据科学与大数据技术  · 2026