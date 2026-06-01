# StudyPilot 智学伴 - AI 智能学习辅助平台

基于 Flask + MySQL + DeepSeek AI 的多用户学习管理 Web 应用，运行于 Windows 11。

## 技术栈

Flask 3.1 / SQLAlchemy 2.0 / MySQL 8.0 / Bootstrap 5 / Chart.js / DeepSeek API

## 项目文档

所有项目标准文档位于 `docs/` 目录：

| 文档 | 路径 | 说明 |
|------|------|------|
| 需求规格 | [docs/requirements.md](docs/requirements.md) | 功能需求详细规格，定义所有功能模块 |
| 技术选型 | [docs/tech-stack.md](docs/tech-stack.md) | 技术栈说明与选型理由 |
| UI设计规范 | [docs/design-spec.md](docs/design-spec.md) | 配色方案、字体、布局、组件风格 |
| 数据库设计 | [docs/database-schema.md](docs/database-schema.md) | 完整建表语句与字段说明（11 张表） |
| 开发步骤 | [docs/development-steps.md](docs/development-steps.md) | 分步执行步骤与验收标准（10 步） |

## 开发日志

每次开发会话结束后，在 `dev_logs/YYYY-MM-DD.md` 中记录：
- 完成的事项
- 遇到的问题及解决方案
- 待办事项
- 下一步计划

## 项目结构

```
studypilot/
├── run.py                    # 应用入口
├── config.py                 # 配置类 (开发/生产/测试)
├── .env                      # 环境变量 (不入git)
├── studypilot/
│   ├── __init__.py           # create_app() 工厂函数
│   ├── models.py             # SQLAlchemy 数据模型
│   ├── extensions.py         # Flask 扩展 (db, migrate, login, mail)
│   ├── utils.py              # 工具函数
│   ├── blueprints/           # 路由蓝图 (每个模块一个文件)
│   ├── services/             # 业务逻辑层
│   ├── static/               # CSS, JS, 上传文件
│   └── templates/            # Jinja2 模板
```

## 开发工作流

1. **启动应用**: `python run.py` → http://127.0.0.1:5000
2. **数据库迁移**:
   ```
   flask db init       # 仅首次
   flask db migrate -m "说明"
   flask db upgrade
   ```
3. **开发配置**: 开发环境邮箱验证打印到控制台（MAIL_SUPPRESS_SEND=True）
4. **分步推进**: 按 `docs/development-steps.md` 的 10 步执行，每步完成后验证

## 重要约定

- 所有模型在单文件 `models.py` 中，便于初学者理解
- AI API 调用使用 openai SDK，base_url 指向 DeepSeek
- 前端用原生 JS + Fetch API 做 AJAX，不引入前端框架
- 全中文 UI 界面
- 淡蓝色主色调 `#4A90D9`
