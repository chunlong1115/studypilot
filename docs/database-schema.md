# StudyPilot 数据库表结构

## 数据库配置

- 数据库名: `studypilot`
- 字符集: `utf8mb4`
- 排序规则: `utf8mb4_unicode_ci`

## 表列表 (11 张)

### users (用户)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | |
| username | VARCHAR(64) | UNIQUE, NOT NULL | 用户名 |
| email | VARCHAR(120) | UNIQUE, NOT NULL | 邮箱 |
| password_hash | VARCHAR(256) | NOT NULL | 密码哈希 |
| avatar | VARCHAR(256) | NULLABLE | 头像路径 |
| is_active | BOOLEAN | DEFAULT FALSE | 邮箱验证后激活 |
| is_admin | BOOLEAN | DEFAULT FALSE | |
| created_at | DATETIME | DEFAULT NOW() | |
| updated_at | DATETIME | ON UPDATE NOW() | |

### learning_preferences (学习偏好)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | |
| user_id | INT | FK→users.id, UNIQUE | |
| subject | VARCHAR(128) | NULLABLE | 学科方向 |
| learning_goal | VARCHAR(256) | NULLABLE | 学习目标 |
| difficulty_level | VARCHAR(32) | NULLABLE | beginner/intermediate/advanced |
| daily_study_minutes | INT | DEFAULT 60 | 每日目标时长 |
| updated_at | DATETIME | DEFAULT NOW() | |

### email_tokens (邮箱令牌)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | |
| user_id | INT | FK→users.id | |
| token | VARCHAR(128) | UNIQUE, NOT NULL | |
| token_type | VARCHAR(32) | NOT NULL | email_verify / password_reset |
| expires_at | DATETIME | NOT NULL | |
| is_used | BOOLEAN | DEFAULT FALSE | |

### materials (学习资料)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | |
| user_id | INT | FK→users.id, NOT NULL | |
| title | VARCHAR(256) | NOT NULL | 资料标题 |
| material_type | VARCHAR(32) | NOT NULL | pdf/note/image/link |
| file_path | VARCHAR(512) | NULLABLE | 上传文件路径 |
| content | TEXT | NULLABLE | 提取文本/笔记内容 |
| url | VARCHAR(1024) | NULLABLE | 链接地址 |
| file_size | INT | NULLABLE | 文件大小(bytes) |
| created_at | DATETIME | DEFAULT NOW() | |
| updated_at | DATETIME | ON UPDATE NOW() | |

### ai_summaries (AI 摘要)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | |
| material_id | INT | FK→materials.id, UNIQUE | |
| summary_text | TEXT | NOT NULL | 摘要内容 |
| key_points | TEXT | NULLABLE | 关键知识点 JSON |
| created_at | DATETIME | DEFAULT NOW() | |

### questions (题目)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | |
| material_id | INT | FK→materials.id | |
| question_type | VARCHAR(32) | NOT NULL | choice/fill_blank/short_answer/true_false |
| question_text | TEXT | NOT NULL | 题目内容 |
| options | TEXT | NULLABLE | 选项 JSON(仅选择题) |
| correct_answer | TEXT | NOT NULL | 正确答案 |
| explanation | TEXT | NULLABLE | 解析 |
| difficulty | VARCHAR(16) | DEFAULT medium | easy/medium/hard |
| created_at | DATETIME | DEFAULT NOW() | |

### user_answers (答题记录)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | |
| user_id | INT | FK→users.id, NOT NULL | |
| question_id | INT | FK→questions.id, NOT NULL | |
| user_answer | TEXT | NOT NULL | 用户答案 |
| is_correct | BOOLEAN | NOT NULL | 是否正确 |
| answered_at | DATETIME | DEFAULT NOW() | |

### error_items (错题本)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | |
| user_id | INT | FK→users.id, NOT NULL | |
| question_id | INT | FK→questions.id | |
| user_answer_id | INT | FK→user_answers.id | |
| review_count | INT | DEFAULT 0 | 复习次数 |
| last_reviewed_at | DATETIME | NULLABLE | |
| next_review_at | DATETIME | NULLABLE | 下次复习时间 |
| mastery_level | INT | DEFAULT 0 | 掌握度 0-5 |
| is_resolved | BOOLEAN | DEFAULT FALSE | 已解决 |
| created_at | DATETIME | DEFAULT NOW() | |

### review_reminders (复习提醒)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | |
| user_id | INT | FK→users.id, NOT NULL | |
| message | VARCHAR(512) | NOT NULL | 提醒内容 |
| reminder_type | VARCHAR(32) | NOT NULL | error_review/daily_study/custom |
| is_read | BOOLEAN | DEFAULT FALSE | |
| created_at | DATETIME | DEFAULT NOW() | |

### learning_sessions (学习记录)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | |
| user_id | INT | FK→users.id, NOT NULL | |
| activity_type | VARCHAR(64) | NOT NULL | study_material/take_quiz/review_error |
| duration_minutes | INT | DEFAULT 0 | |
| material_id | INT | FK→materials.id, NULLABLE | |
| notes | VARCHAR(256) | NULLABLE | |
| created_at | DATETIME | DEFAULT NOW() | |
