"""FastAPI Application for NexaData AI."""
import sys
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response, StreamingResponse

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.models import ChatRequest, ChatResponse, BrandInfoResponse, PromptChip, ExportPdfRequest, ConversationMessage
from backend.orchestrator import orchestrator
from backend.pdf_exporter import generate_conversation_pdf
from backend.file_handler import process_uploaded_file, validate_file, MAX_FILE_SIZE_BYTES
from database.postgres import (
    get_products_list,
    get_master_records_list,
    get_customers_list,
    get_orders_list,
    get_inventory_list,
    get_departments_list,
    get_employees_list,
    get_policies_list,
    get_faqs_list,
    get_transactions_list,
    get_analytics_summary,
    search_records,
    db_engine
)
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
    Supports optional temporary attachment payload and multi-turn conversation history.
    """
    try:
        response = orchestrator.process_message(
            message=request.message.strip(),
            mode=request.mode,
            attachment=request.attachment,
            conversation_history=request.conversation_history
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat-stream")
def chat_stream_endpoint(request: ChatRequest):
    """
    Real-time Token Streaming endpoint using Server-Sent Events (SSE).
    Streams LLM tokens progressively to eliminate the blank delay.
    Yields data: {"token": "..."} chunks and finishes with data: {"done": true, ...}.
    """
    try:
        return StreamingResponse(
            orchestrator.stream_message(
                message=request.message.strip(),
                mode=request.mode,
                attachment=request.attachment,
                conversation_history=request.conversation_history
            ),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat-upload", response_model=ChatResponse)
async def chat_upload_endpoint(
    message: str = Form(""),
    mode: str = Form("company"),
    session_id: Optional[str] = Form(None),
    conversation_history: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    """
    Dual-mode chat endpoint with direct multipart file or image upload.
    Validates file format and size (<= 10 MB) and processes in-memory.
    Uploads remain strictly temporary and are not added to the permanent knowledge base.
    """
    try:
        parsed_history = []
        if conversation_history:
            import json
            try:
                raw_list = json.loads(conversation_history)
                if isinstance(raw_list, list):
                    for item in raw_list:
                        if isinstance(item, dict) and "role" in item and "content" in item:
                            parsed_history.append(ConversationMessage(role=item["role"], content=str(item["content"])))
            except Exception:
                pass

        attachment_data = None
        if file and file.filename:
            file_bytes = await file.read()
            try:
                attachment_data = process_uploaded_file(file.filename, file_bytes)
            except ValueError as ve:
                raise HTTPException(status_code=400, detail=str(ve))
            except Exception as fe:
                raise HTTPException(status_code=400, detail=f"Failed to process file '{file.filename}': {str(fe)}")

        response = orchestrator.process_message(
            message=message.strip(),
            mode=mode,
            attachment=attachment_data,
            conversation_history=parsed_history
        )
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload-preview")
async def upload_preview_endpoint(file: UploadFile = File(...)):
    """
    Client pre-validation and preview endpoint for attached files/images.
    """
    try:
        file_bytes = await file.read()
        res = process_uploaded_file(file.filename, file_bytes)
        return {
            "status": "valid",
            "filename": res["filename"],
            "extension": res["extension"],
            "size_bytes": res["size_bytes"],
            "size_formatted": res["size_formatted"],
            "is_image": res["is_image"],
            "is_document": res["is_document"],
            "summary": res.get("summary", ""),
            "metadata": res.get("metadata", {})
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# ============================================================================
# 🎙️ Speech-to-Text Transcription Endpoint (OpenAI Whisper & Fallback)
# ============================================================================
@app.post("/api/transcribe")
async def transcribe_audio_endpoint(
    file: UploadFile = File(...),
    language: Optional[str] = Form("en")
):
    """
    Transcribe speech audio recording (webm/wav/mp3/m4a) to text.
    Supports English ('en') and Hindi ('hi').
    Uses OpenAI Whisper when configured, with safe offline fallback.
    """
    try:
        audio_bytes = await file.read()
        if not audio_bytes:
            raise HTTPException(status_code=400, detail="Empty audio recording.")

        # If OpenAI client available, invoke Whisper API
        if orchestrator.client:
            try:
                whisper_lang = "hi" if language and language.startswith("hi") else "en"
                audio_file = (file.filename or "recording.webm", audio_bytes, file.content_type or "audio/webm")
                transcription = orchestrator.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=whisper_lang
                )
                return {
                    "status": "success",
                    "text": transcription.text.strip(),
                    "language": whisper_lang,
                    "provider": "whisper"
                }
            except Exception as we:
                pass

        return {
            "status": "offline",
            "text": "",
            "language": language or "en",
            "provider": "offline",
            "message": "Audio received. For server-side Whisper transcription, configure OPENAI_API_KEY in .env."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


# ============================================================================
# 📄 Conversation PDF Download Endpoint
# ============================================================================
@app.post("/api/export-pdf")
def export_pdf_endpoint(payload: ExportPdfRequest):
    """
    Generate and download a branded PDF transcript of the conversation.
    """
    try:
        pdf_bytes = generate_conversation_pdf(
            title=payload.title or "NexaData Conversation",
            mode=payload.mode or "company",
            messages=payload.messages or [],
            export_time=payload.export_time
        )
        clean_title = "".join(c for c in (payload.title or "Chat") if c.isalnum() or c in (" ", "_", "-")).strip()
        filename = f"NexaData_{clean_title.replace(' ', '_')}.pdf"

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate conversation PDF: {str(e)}")

# ============================================================================
# 🗄️ PostgreSQL Database Demonstration & Query Endpoints
# ============================================================================
@app.get("/api/db/status")
def get_db_status():
    """Returns database connection status and analytics summary."""
    return get_analytics_summary()

@app.get("/api/db/products")
def get_products():
    """Retrieve all product catalog records (24 records)."""
    return {"products": get_products_list()}

@app.get("/api/db/masters")
def get_masters():
    """Retrieve all client master records."""
    return {"clients": get_master_records_list()}

@app.get("/api/db/customers")
def get_customers(limit: int = 100, tier: Optional[str] = None, status: Optional[str] = None):
    """Retrieve customer accounts (55 records)."""
    return {"customers": get_customers_list(limit=limit, tier=tier, status=status)}

@app.get("/api/db/orders")
def get_orders(limit: int = 50, customer_code: Optional[str] = None, status: Optional[str] = None):
    """Retrieve customer orders (115 records)."""
    return {"orders": get_orders_list(limit=limit, customer_code=customer_code, status=status)}

@app.get("/api/db/inventory")
def get_inventory(limit: int = 50, low_stock_only: bool = False):
    """Retrieve inventory and stock records."""
    return {"inventory": get_inventory_list(limit=limit, low_stock_only=low_stock_only)}

@app.get("/api/db/departments")
def get_departments():
    """Retrieve corporate departments."""
    return {"departments": get_departments_list()}

@app.get("/api/db/employees")
def get_employees(limit: int = 50, department_code: Optional[str] = None):
    """Retrieve staff employee directory."""
    return {"employees": get_employees_list(limit=limit, department_code=department_code)}

@app.get("/api/db/policies")
def get_policies(category: Optional[str] = None):
    """Retrieve official corporate policies."""
    return {"policies": get_policies_list(category=category)}

@app.get("/api/db/faqs")
def get_faqs(category: Optional[str] = None):
    """Retrieve knowledge base FAQs."""
    return {"faqs": get_faqs_list(category=category)}

@app.get("/api/db/transactions")
def get_transactions(limit: int = 50, client_code: str = None, status: str = None):
    """Retrieve business transactions (215 records)."""
    return {"transactions": get_transactions_list(limit=limit, client_code=client_code, status=status)}

@app.get("/api/db/search")
def search_db(q: str):
    """Search records across products, customers, transactions, inventory, and policies."""
    return search_records(q)


