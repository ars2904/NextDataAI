"""Request and Response Pydantic models for NexaData AI API."""
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field

class SourceCitation(BaseModel):
    document: str
    page: int
    score: float
    snippet: str

class ConversationMessage(BaseModel):
    role: Literal["user", "assistant", "system"] = Field("user", description="Message author role")
    content: str = Field(..., description="Message text content")

class ChatRequest(BaseModel):
    message: str = Field("", description="User's query (can be empty if attachment provided)")
    mode: Literal["general", "company"] = Field("company", description="Active chat mode")
    session_id: Optional[str] = Field(None, description="Optional session/conversation identifier")
    attachment: Optional[Dict[str, Any]] = Field(None, description="Optional attached file payload")
    conversation_history: Optional[List[ConversationMessage]] = Field(default=[], description="Previous conversation turns for multi-turn context")

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

class RegisterRequest(BaseModel):
    email: str = Field(..., description="User's email address")
    password: str = Field(..., min_length=6, description="Plaintext password (min 6 chars)")
    full_name: str = Field(..., min_length=1, description="User's full name")

class LoginRequest(BaseModel):
    email: str = Field(..., description="User's email address")
    password: str = Field(..., description="Plaintext password")

class UserProfile(BaseModel):
    user_id: str
    email: str
    full_name: str
    role: str = "user"
    is_active: bool = True
    created_at: Optional[str] = None
    last_login_at: Optional[str] = None

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfile

