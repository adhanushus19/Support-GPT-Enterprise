import os
import json
from bs4 import BeautifulSoup
import PyPDF2
import docx

def extract_pdf_text(file_path: str) -> str:
    """Extract text from a PDF file."""
    text_content = []
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text = page.extract_text()
            if text:
                text_content.append(text)
    return "\n".join(text_content)

def extract_docx_text(file_path: str) -> str:
    """Extract text from a DOCX file."""
    doc = docx.Document(file_path)
    text_content = [p.text for p in doc.paragraphs]
    return "\n".join(text_content)

def extract_html_text(file_path: str) -> str:
    """Extract text from an HTML file using BeautifulSoup."""
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        return soup.get_text(separator="\n")

def parse_faq_json(file_path: str) -> list:
    """
    Parse a JSON FAQ file.
    Expected format: [{"question": "...", "answer": "...", "category": "..."}]
    """
    with open(file_path, "r", encoding="utf-8") as f:
        faqs = json.load(f)
    return faqs

def extract_text_from_file(file_path: str) -> str:
    """Router function to extract raw text content based on file extension."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_pdf_text(file_path)
    elif ext == ".docx":
        return extract_docx_text(file_path)
    elif ext in [".html", ".htm"]:
        return extract_html_text(file_path)
    elif ext in [".txt", ".md"]:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        raise ValueError(f"Unsupported file type: {ext}")
