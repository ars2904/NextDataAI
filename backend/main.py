"""FastAPI Application for NexaData AI."""
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.models import ChatRequest, ChatResponse, BrandInfoResponse, PromptChip
from backend.orchestrator import orchestrator
from rag.engine import knowledge_base

FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(
    title="NexaData AI API",
    description="Dual-Mode Conversational API (General LLM & Company PDF RAG)",
    version="1.0.0"
)

# Enable CORS for external embeddable website widget support
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static frontend directory
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

@app.get("/")
def serve_index():
    """Serve the standalone NexaData web application."""
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "NexaData AI API online. Frontend index.html not found."}

@app.get("/logo.png")
def serve_logo():
    """Direct route for official NexaData AI logo badge."""
    logo_file = BASE_DIR / "NexaData AI_ Ask_Analyze_Discover.png"
    if logo_file.exists():
        return FileResponse(str(logo_file), media_type="image/png")
    return FileResponse(str(FRONTEND_DIR / "logo.png"), media_type="image/png")

@app.get("/api/health")
def health_check():
    """Health check and readiness probe."""
    return {
        "status": "online",
        "app": "NexaData AI",
        "indexed_documents": len(knowledge_base.indexed_files),
        "total_chunks": len(knowledge_base.chunks)
    }

@app.get("/api/info", response_model=BrandInfoResponse)
def get_brand_info():
    """Returns NexaData branding metadata and starter prompts."""
    return BrandInfoResponse(
        company_name="NexaData AI",
        tagline="Ask. Analyze. Discover.",
        subtitle="Autonomous AI Data Analytics & Enterprise Intelligence",
        prompt_chips=[
            PromptChip(label="What is NexaData?", prompt="What is NexaData and what are its core capabilities?"),
            PromptChip(label="Our Solutions", prompt="What are the available data solutions and services?"),
            PromptChip(label="How does it work?", prompt="How does the AI analysis and query system work?"),
            PromptChip(label="Platform Policies", prompt="What are the data privacy and platform policies?")
        ],
        indexed_documents=knowledge_base.indexed_files,
        total_document_chunks=len(knowledge_base.chunks)
    )

@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    """
    Dual-mode chat endpoint:
    - mode="company": Queries VedaNova PDF knowledge base via RAG.
    - mode="general": Open conversational AI.
    """
    try:
        response = orchestrator.process_message(
            message=request.message.strip(),
            mode=request.mode
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
