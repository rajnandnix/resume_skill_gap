import PyPDF2

def extract_resume_text(file):
    reader = PyPDF2.PdfReader(file)
    text_parts = []

    for page in reader.pages:
        page_text = page.extract_text() or ""
        if page_text.strip():
            text_parts.append(page_text)

    return "\n".join(text_parts).strip()