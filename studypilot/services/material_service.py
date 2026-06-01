"""学习资料处理服务."""
from flask import current_app


def extract_pdf_text(filepath):
    """使用 PyMuPDF 提取 PDF 文本内容，容错处理."""
    try:
        import fitz
        doc = fitz.open(filepath)
        text_parts = []
        for page_num in range(len(doc)):
            try:
                page = doc[page_num]
                page_text = page.get_text()
                if page_text.strip():
                    text_parts.append(page_text.strip())
            except Exception:
                continue
        doc.close()

        extracted = '\n'.join(text_parts).strip()
        if not extracted:
            current_app.logger.warning(f"PDF 未能提取文本内容: {filepath}")
        return extracted
    except Exception as e:
        current_app.logger.error(f"PDF 解析失败: {e}")
        return ''
