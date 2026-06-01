# StudyPilot 技术选型说明

## 技术栈

| 层级 | 技术 | 版本 | 选型理由 |
|------|------|------|----------|
| 后端框架 | Flask | 3.1.x | 轻量、灵活、适合初学者 |
| ORM | SQLAlchemy + Flask-SQLAlchemy | 2.0.x / 3.1.x | 简化数据库操作，支持 MySQL |
| 数据库迁移 | Flask-Migrate | 4.1.x | 数据库版本管理 |
| 认证 | Flask-Login | 0.6.x | Session 管理，登录状态维护 |
| 邮件 | Flask-Mail | 0.10.x | 邮箱验证、密码重置 |
| 数据库 | MySQL | 8.0+ | 用户要求；需配置 utf8mb4 |
| MySQL驱动 | PyMySQL | 1.1.x | 纯 Python 实现，跨平台 |
| AI SDK | openai | 1.x | DeepSeek API 兼容 OpenAI 格式 |
| PDF解析 | PyMuPDF (fitz) | 1.25.x | 中文支持好、速度快 |
| 图片处理 | Pillow | 11.x | 头像处理、图片上传 |
| 前端框架 | Bootstrap 5 | CDN | 无需构建工具，响应式布局 |
| 图表 | Chart.js | 4.4.x | 轻量图表库 |
| 图标 | Bootstrap Icons | CDN | 丰富图标集 |
| 配置管理 | python-dotenv | 1.1.x | 环境变量加载 |
| 日期工具 | python-dateutil | 2.9.x | 间隔重复算法日期计算 |

## 架构设计

```
前端 (HTML + Bootstrap + JS + Chart.js)
        ↓ HTTP
Flask 路由层 (Blueprints)
        ↓
业务逻辑层 (Services)
        ↓
AI 接口层 (DeepSeek API / openai SDK)
        ↓
数据层 (SQLAlchemy ORM → MySQL)
```

## 不使用但常见的技术（及原因）

| 技术 | 跳过理由 |
|------|----------|
| Celery + Redis | 异步任务增加复杂度，AJAX 同步调用已满足需求 |
| Vue/React | 增加构建工具链，原生 JS 对当前规模足够 |
| Docker | 初学者 Windows 环境，本地直接运行更简单 |
| Nginx | 个人项目，Flask 开发服务器即可 |
