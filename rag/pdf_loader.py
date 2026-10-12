"""PDF Document Extractor for VedaNova Company Knowledge Base."""
from pathlib import Path
from typing import List, Dict, Any
import pypdf

def extract_text_from_pdf(pdf_path: Path) -> List[Dict[str, Any]]:
    """
    Extract text from a PDF file page by page.
    Returns a list of dicts: [{"page": 1, "text": "...", "source": "filename.pdf"}, ...]
    """
    results = []
    reader = pypdf.PdfReader(str(pdf_path))
    for idx, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        cleaned_text = " ".join(text.split())
        if cleaned_text:
            results.append({
                "page": idx + 1,
                "text": cleaned_text,
                "source": pdf_path.name,
                "source_path": str(pdf_path)
            })
    return results

def load_all_company_docs(docs_dir: Path) -> List[Dict[str, Any]]:
    """
    Scan the company_docs folder and extract all PDF documents.
    """
    all_pages = []
    if not docs_dir.exists():
        return all_pages
        
    for pdf_file in docs_dir.glob("*.pdf"):
        pages = extract_text_from_pdf(pdf_file)
        all_pages.extend(pages)
        
    return all_pages
