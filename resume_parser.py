import PyPDF2

def extract_resume_text(file):
    try:
        reader = PyPDF2.PdfReader(file)
    except Exception:
        return ""
    text_parts = []

    for page in reader.pages:
        try:
            page_text = page.extract_text() or ""
        except Exception:
            page_text = ""
        if page_text.strip():
            text_parts.append(page_text)

    return "\n".join(text_parts).strip()