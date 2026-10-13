"""Secure file and image handler for NexaData AI.
Supports PDF, DOCX, TXT, CSV, PNG, JPG, JPEG, and WEBP up to 10 MB.
Processes files temporarily in-memory with strict validation and cleanup.
"""
import io
import re
import base64
import zipfile
import xml.etree.ElementTree as ET
from typing import Dict, Any, Tuple, Optional
from PIL import Image
import pandas as pd
from pypdf import PdfReader

# Maximum file size: 10 MB
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024

SUPPORTED_EXTENSIONS = {
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "txt": "text/plain",
    "csv": "text/csv",
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "webp": "image/webp",
}

IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
DOCUMENT_EXTENSIONS = {"pdf", "docx", "txt", "csv"}


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal or unsafe characters."""
    if not filename:
        return "uploaded_file"
    # Remove path prefixes
    clean = filename.replace("\\", "/").split("/")[-1]
    # Replace non-alphanumeric except dots, dashes, underscores
    clean = re.sub(r"[^a-zA-Z0-9._-]", "_", clean)
    return clean[:120] if clean else "uploaded_file"


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable units."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def validate_file(filename: str, file_bytes: bytes) -> Tuple[bool, str, str]:
    """
    Validate file extension, size, and magic bytes.
    Returns: (is_valid, error_message, file_extension)
    """
    if not file_bytes:
        return False, "Uploaded file is empty (0 bytes).", ""

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        max_mb = MAX_FILE_SIZE_BYTES / (1024 * 1024)
        return False, f"File size exceeds the {max_mb:.0f} MB limit. File is {format_file_size(len(file_bytes))}.", ""

    ext = filename.lower().split(".")[-1] if "." in filename else ""
    if ext not in SUPPORTED_EXTENSIONS:
        supported_list = ", ".join(SUPPORTED_EXTENSIONS.keys()).upper()
        return False, f"Unsupported file format '.{ext}'. Supported formats are: {supported_list}.", ""

    return True, "", ext


def extract_pdf_text(file_bytes: bytes, max_pages: int = 50, max_chars: int = 50000) -> Tuple[str, Dict[str, Any]]:
    """Extract text from PDF using pypdf."""
    reader = PdfReader(io.BytesIO(file_bytes))
    total_pages = len(reader.pages)
    text_parts = []
    total_chars = 0

    for idx, page in enumerate(reader.pages[:max_pages]):
        extracted = page.extract_text() or ""
        if extracted.strip():
            text_parts.append(f"--- Page {idx + 1} ---\n{extracted.strip()}")
            total_chars += len(extracted)
            if total_chars >= max_chars:
                text_parts.append(f"\n[Truncated: Exceeded {max_chars} character limit across {idx + 1} pages]")
                break

    full_text = "\n\n".join(text_parts)
    if not full_text.strip():
        full_text = "(Note: This PDF appears to be scanned or contains only images/vector drawings with no selectable text.)"

    meta = {
        "total_pages": total_pages,
        "processed_pages": min(total_pages, max_pages),
        "char_count": len(full_text)
    }
    return full_text, meta


def extract_docx_text(file_bytes: bytes, max_chars: int = 50000) -> Tuple[str, Dict[str, Any]]:
    """Extract text from DOCX using standard zipfile and xml parser (no external library required)."""
    with zipfile.ZipFile(io.BytesIO(file_bytes)) as docx_zip:
        xml_content = docx_zip.read("word/document.xml")
        tree = ET.fromstring(xml_content)
        
        # XML namespace for wordprocessingml
        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        paragraphs = []
        total_chars = 0
        
        for p in tree.iter(f"{{{ns['w']}}}p"):
            texts = [node.text for node in p.iter(f"{{{ns['w']}}}t") if node.text]
            if texts:
                p_text = "".join(texts).strip()
                if p_text:
                    paragraphs.append(p_text)
                    total_chars += len(p_text)
                    if total_chars >= max_chars:
                        paragraphs.append(f"\n[Truncated: Exceeded {max_chars} character limit]")
                        break

    full_text = "\n\n".join(paragraphs)
    if not full_text.strip():
        full_text = "(The DOCX document is empty or contains no readable paragraphs.)"

    meta = {
        "paragraph_count": len(paragraphs),
        "char_count": len(full_text)
    }
    return full_text, meta


def extract_txt_text(file_bytes: bytes, max_chars: int = 50000) -> Tuple[str, Dict[str, Any]]:
    """Extract text from plain text file with multi-encoding fallback."""
    for enc in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
        try:
            text = file_bytes.decode(enc)
            if len(text) > max_chars:
                text = text[:max_chars] + f"\n\n[Truncated: Exceeded {max_chars} character limit]"
            return text, {"encoding": enc, "char_count": len(text)}
        except UnicodeDecodeError:
            continue
    text = file_bytes.decode("utf-8", errors="replace")[:max_chars]
    return text, {"encoding": "utf-8-replace", "char_count": len(text)}


def extract_csv_summary(file_bytes: bytes, max_rows: int = 20) -> Tuple[str, Dict[str, Any]]:
    """Extract rich structured summary and statistics from CSV file using pandas."""
    try:
        df = pd.read_csv(io.BytesIO(file_bytes))
    except Exception:
        # Fallback to latin-1
        df = pd.read_csv(io.BytesIO(file_bytes), encoding="latin-1")

    rows_count, cols_count = df.shape
    col_names = list(df.columns)
    
    # Missing values
    missing = df.isnull().sum().to_dict()
    missing_summary = [f"{col}: {cnt} missing" for col, cnt in missing.items() if cnt > 0]
    missing_str = ", ".join(missing_summary) if missing_summary else "No missing values"

    # Numeric summary
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    stats_summary = ""
    if numeric_cols:
        desc = df[numeric_cols].describe().round(2).to_string()
        stats_summary = f"\n\n### Numeric Columns Summary:\n```\n{desc}\n```"

    # Top sample rows
    sample_preview = df.head(min(max_rows, rows_count)).to_string(index=False)

    summary_text = (
        f"### CSV Dataset Overview\n"
        f"- **Rows:** {rows_count:,}\n"
        f"- **Columns ({cols_count}):** {', '.join(col_names[:15])}{'...' if len(col_names) > 15 else ''}\n"
        f"- **Data Completeness:** {missing_str}\n"
        f"{stats_summary}\n\n"
        f"### Sample Records (Top {min(max_rows, rows_count)}):\n"
        f"```\n{sample_preview}\n```"
    )

    meta = {
        "rows": rows_count,
        "columns": cols_count,
        "column_names": col_names,
        "numeric_columns": numeric_cols
    }
    return summary_text, meta


def process_image(file_bytes: bytes, filename: str, ext: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Validate image and prepare base64 representation for vision models."""
    img = Image.open(io.BytesIO(file_bytes))
    width, height = img.size
    fmt = img.format or ext.upper()
    
    mime_type = SUPPORTED_EXTENSIONS.get(ext, f"image/{ext}")
    b64_str = base64.b64encode(file_bytes).decode("utf-8")

    meta = {
        "width": width,
        "height": height,
        "format": fmt,
        "aspect_ratio": f"{width}:{height}"
    }

    image_data = {
        "b64_image": b64_str,
        "mime_type": mime_type,
        "dimensions": (width, height),
        "summary": f"Image ({fmt}, {width}x{height} px, {format_file_size(len(file_bytes))})"
    }
    return image_data, meta


def process_uploaded_file(filename: str, file_bytes: bytes) -> Dict[str, Any]:
    """
    Main entrypoint to validate and process an uploaded file or image in-memory.
    Returns structured dictionary with extracted text or image payload.
    """
    clean_name = sanitize_filename(filename)
    is_valid, err_msg, ext = validate_file(clean_name, file_bytes)
    
    if not is_valid:
        raise ValueError(err_msg)

    size_formatted = format_file_size(len(file_bytes))
    result: Dict[str, Any] = {
        "filename": clean_name,
        "extension": ext,
        "size_bytes": len(file_bytes),
        "size_formatted": size_formatted,
        "is_image": ext in IMAGE_EXTENSIONS,
        "is_document": ext in DOCUMENT_EXTENSIONS,
        "text_content": "",
        "b64_image": None,
        "mime_type": SUPPORTED_EXTENSIONS.get(ext, "application/octet-stream"),
        "metadata": {}
    }

    if ext in IMAGE_EXTENSIONS:
        img_data, meta = process_image(file_bytes, clean_name, ext)
        result["b64_image"] = img_data["b64_image"]
        result["mime_type"] = img_data["mime_type"]
        result["metadata"] = meta
        result["summary"] = img_data["summary"]
    elif ext == "pdf":
        text, meta = extract_pdf_text(file_bytes)
        result["text_content"] = text
        result["metadata"] = meta
        result["summary"] = f"PDF Document ({meta['total_pages']} pages, {size_formatted})"
    elif ext == "docx":
        text, meta = extract_docx_text(file_bytes)
        result["text_content"] = text
        result["metadata"] = meta
        result["summary"] = f"Word Document ({meta['paragraph_count']} paragraphs, {size_formatted})"
    elif ext == "txt":
        text, meta = extract_txt_text(file_bytes)
        result["text_content"] = text
        result["metadata"] = meta
        result["summary"] = f"Text Document ({meta['char_count']:,} characters, {size_formatted})"
    elif ext == "csv":
        text, meta = extract_csv_summary(file_bytes)
        result["text_content"] = text
        result["metadata"] = meta
        result["summary"] = f"CSV Dataset ({meta['rows']:,} rows x {meta['columns']} cols, {size_formatted})"

    return result
