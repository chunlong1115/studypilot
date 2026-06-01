"""DeepSeek AI 服务 - 摘要生成 & 题目生成."""
import json
import re
from flask import current_app
from openai import OpenAI


def _get_client():
    """获取 DeepSeek API 客户端."""
    return OpenAI(
        api_key=current_app.config['DEEPSEEK_API_KEY'],
        base_url=current_app.config['DEEPSEEK_BASE_URL'],
    )


def call_deepseek(messages, temperature=0.7, max_tokens=4096):
    """调用 DeepSeek API, 返回响应文本."""
    client = _get_client()
    model = current_app.config['DEEPSEEK_MODEL']

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
    except Exception as e:
        current_app.logger.error(f"DeepSeek API 调用失败: {e}")
        raise


# ============================================================
# 摘要生成
# ============================================================

SUMMARY_PROMPT = """你是一位学习助手。请为以下学习材料生成摘要和关键知识点。

材料内容：
{content}

请用中文回复，格式如下：

【摘要】
（200字以内的内容摘要）

【关键知识点】
1. 知识点一
2. 知识点二
3. 知识点三
...（3-8个关键知识点）"""


def generate_summary(content_text, user_prefs=None):
    """生成学习资料摘要."""
    if not content_text or len(content_text.strip()) < 20:
        return '内容太短，无法生成摘要。', ''

    # 截取内容防止超 token 限制
    if len(content_text) > 8000:
        content_text = content_text[:8000] + '...(内容已截断)'

    prompt = SUMMARY_PROMPT.format(content=content_text)
    if user_prefs and user_prefs.get('subject'):
        prompt += f'\n\n注意：用户学科为"{user_prefs["subject"]}"，难度偏好"{user_prefs.get("difficulty_level", "beginner")}"。'

    try:
        response = call_deepseek([{"role": "user", "content": prompt}])
        # 解析返回
        summary_match = re.search(r'【摘要】\s*\n?(.*?)(?=【关键知识点】|$)', response, re.DOTALL)
        keypoints_match = re.search(r'【关键知识点】\s*\n?(.*?)$', response, re.DOTALL)

        summary = summary_match.group(1).strip() if summary_match else response
        key_points = keypoints_match.group(1).strip() if keypoints_match else ''

        return summary, key_points
    except Exception:
        return 'AI 摘要生成失败，请稍后重试。', ''


# ============================================================
# 题目生成
# ============================================================

QUIZ_PROMPT = """你是一位出题老师。请根据以下学习材料生成练习题。

材料内容：
{content}

要求：
- 总共生成 {count} 道题目
- 题型包括：{types}
- 难度：{difficulty}
- 每道题附带答案和解析

请严格按以下 JSON 格式回复（不要回复其他内容）：
```json
[
  {{
    "type": "choice",
    "question": "题目内容",
    "options": ["A. 选项一", "B. 选项二", "C. 选项三", "D. 选项四"],
    "answer": "B",
    "explanation": "解析内容",
    "difficulty": "easy"
  }},
  {{
    "type": "fill_blank",
    "question": "Python 中列表使用_____定义。",
    "answer": "方括号 []",
    "explanation": "列表是 Python 中最常用的数据结构之一。",
    "difficulty": "medium"
  }},
  {{
    "type": "true_false",
    "question": "Python 是一种编译型语言。",
    "answer": "错误",
    "explanation": "Python 是解释型语言。",
    "difficulty": "easy"
  }},
  {{
    "type": "short_answer",
    "question": "请简述 Python 中列表和元组的区别。",
    "answer": "列表可变，元组不可变；列表使用方括号，元组使用圆括号。",
    "explanation": "这是 Python 基础中重要的区别。",
    "difficulty": "medium"
  }}
]
```

重要提示：
- choice 题型必须提供 options 数组(4个选项)
- fill_blank 题型的 answer 是填写的正确内容
- true_false 题型的 answer 是"正确"或"错误"
- short_answer 题型的 answer 是要点回答
- 每道题都必须有 explanation(解析)"""


def generate_quiz(content_text, count=5, question_types=None, difficulty='medium', user_prefs=None):
    """生成练习题, 返回题目列表."""
    if not content_text or len(content_text.strip()) < 50:
        raise ValueError('资料内容太短，无法生成题目。请提供更详细的学习材料。')

    if len(content_text) > 6000:
        content_text = content_text[:6000] + '...(内容已截断)'

    if not question_types:
        question_types = ['choice', 'fill_blank', 'true_false', 'short_answer']

    types_str = '、'.join(question_types)

    prompt = QUIZ_PROMPT.format(
        content=content_text,
        count=count,
        types=types_str,
        difficulty=difficulty,
    )

    if user_prefs and user_prefs.get('subject'):
        prompt += f'\n注意：用户学科为"{user_prefs["subject"]}"，请围绕该学科出题。'

    try:
        response = call_deepseek([{"role": "user", "content": prompt}], temperature=0.8, max_tokens=4096)

        # 提取 JSON
        json_match = re.search(r'```json\s*\n?(.*?)```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # 尝试直接解析整个响应
            json_str = response.strip().lstrip('[').rstrip(']')
            if not json_str.startswith('['):
                json_str = '[' + json_str + ']'

        questions = json.loads(json_str)
        return questions

    except json.JSONDecodeError as e:
        current_app.logger.error(f"题目 JSON 解析失败: {e}, 原始响应: {response[:500]}")
        raise ValueError('AI 返回格式异常，请重试。')
    except Exception as e:
        current_app.logger.error(f"题目生成失败: {e}")
        raise
