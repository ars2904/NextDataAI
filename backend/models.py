"""Request and Response Pydantic models for NexaData AI API."""
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field

class SourceCitation(BaseModel):
    document: str
    page: int
    score: float
    snippet: str

class ChatRequest(BaseModel):
    message: str = Field("", description="User's query (can be empty if attachment provided)")
    mode: Literal["general", "company"] = Field("company", description="Active chat mode")
    session_id: Optional[str] = Field(None, description="Optional session/conversation identifier")
    attachment: Optional[Dict[str, Any]] = Field(None, description="Optional attached file payload")

class ChatResponse(BaseModel):
    reply: str
    mode: str
    sources: List[SourceCitation] = []
    timestamp: str
    attachment_info: Optional[Dict[str, Any]] = None

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

class ExportPdfRequest(BaseModel):
    title: Optional[str] = "NexaData Conversation"
    mode: Optional[str] = "company"
    messages: List[Dict[str, Any]] = []
    export_time: Optional[str] = None
