"""Request and Response Pydantic models for NexaData AI API."""
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field

class SourceCitation(BaseModel):
    document: str
    page: int
    score: float
    snippet: str

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User's query")
    mode: Literal["general", "company"] = Field("company", description="Active chat mode")
    session_id: Optional[str] = Field(None, description="Optional session/conversation identifier")

class ChatResponse(BaseModel):
    reply: str
    mode: str
    sources: List[SourceCitation] = []
    timestamp: str

class PromptChip(BaseModel):
    label: str
    prompt: str

class BrandInfoResponse(BaseModel):
    company_name: str
    tagline: str
    subtitle: str
    prompt_chips: List[PromptChip]
    indexed_documents: List[str]
    total_document_chunks: int
