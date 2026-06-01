# StudyPilot 分步开发执行步骤

## 第 1 步：项目骨架搭建 ✅ 当前步骤
- [x] 创建目录结构
- [x] requirements.txt + 安装依赖
- [x] config.py / .env.example / .env
- [x] studypilot/__init__.py (app 工厂)
- [x] studypilot/extensions.py
- [x] run.py
- [x] base.html + style.css
- [x] index.html 着陆页
- [ ] 依赖安装 + 启动验证

## 第 2 步：数据库 + 用户认证
- 安装 MySQL，创建数据库
- models.py 全部模型
- Flask-Migrate 初始化
- auth.py 蓝图
- 邮箱验证 / 密码重置
- 认证相关模板

## 第 3 步：用户中心
- user.py 蓝图
- 个人信息修改
- 学习偏好设置

## 第 4 步：仪表盘
- main.py 仪表盘路由
- 统计卡片

## 第 5 步：学习资料管理
- materials.py 蓝图
- PDF 上传 + 解析
- 笔记 / 图片 / 链接

## 第 6 步：AI 摘要
- services/ai_service.py
- 摘要生成

## 第 7 步：AI 出题 + 答题
- AI 出题
- quiz.py 蓝图

## 第 8 步：错题本
- errors.py 蓝图
- 间隔重复复习

## 第 9 步：学习进度 + 提醒
- progress.py 蓝图
- review.py 蓝图

## 第 10 步：打磨完善
- UI 统一
- 文案校对
- 全流程测试
