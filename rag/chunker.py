"""Semantic Text Chunker with Metadata Tracking."""
from typing import List, Dict, Any

def chunk_document_pages(
    pages: List[Dict[str, Any]],
    chunk_size: int = 500,
    chunk_overlap: int = 100
) -> List[Dict[str, Any]]:
    """
    Split extracted pages into overlapping text chunks, retaining source and page info.
    """
    chunks = []
    chunk_id = 0

    for page_info in pages:
        text = page_info["text"]
        source = page_info["source"]
        page_num = page_info["page"]

        # Word-based sliding window
        words = text.split()
        if len(words) <= chunk_size:
            chunk_id += 1
            chunks.append({
                "chunk_id": chunk_id,
                "text": text,
                "source": source,
                "page": page_num,
                "word_count": len(words)
            })
            continue

        start = 0
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)
            
            chunk_id += 1
            chunks.append({
                "chunk_id": chunk_id,
                "text": chunk_text,
                "source": source,
                "page": page_num,
                "word_count": len(chunk_words)
            })
            
            if end == len(words):
                break
            start += (chunk_size - chunk_overlap)

    return chunks
