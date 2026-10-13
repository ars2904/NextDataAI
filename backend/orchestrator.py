"""Chat Orchestrator for Dual-Mode Conversation."""
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from rag.engine import knowledge_base
from backend.models import SourceCitation, ChatResponse
from database.postgres import query_database_smart

load_dotenv()

class ChatOrchestrator:
    """
    Coordinates between General Model, Company PDF RAG Engine, and PostgreSQL Database.
    """
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.client = None
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except Exception:
                self.client = None

    def _get_timestamp(self) -> str:
        return datetime.now().strftime("%I:%M %p")

    def handle_company_question(self, message: str, attachment: Optional[Dict[str, Any]] = None) -> ChatResponse:
        """Query company PDF documents using RAG or direct database records, with optional temporary attachment."""
        attachment_sources = []
        attachment_info = None

        if attachment:
            attachment_info = {
                "filename": attachment.get("filename"),
                "summary": attachment.get("summary"),
                "is_image": attachment.get("is_image", False),
                "size_formatted": attachment.get("size_formatted")
            }
            label = "Attached Image" if attachment.get("is_image") else "Attached File"
            attachment_sources.append(SourceCitation(
                document=f"{label}: {attachment.get('filename')}",
                page=1,
                score=1.0,
                snippet=attachment.get("summary", "User uploaded temporary attachment")
            ))

            # If user uploaded an image in company mode
            if attachment.get("is_image"):
                prompt_text = message.strip() if message.strip() else "Analyze this image in the context of NexaData operations, describe its contents, and explain key takeaways."
                if self.client:
                    try:
                        response = self.client.chat.completions.create(
                            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                            messages=[
                                {
                                    "role": "system",
                                    "content": (
                                        "You are NexaData AI. Analyze the uploaded image. "
                                        "Relate the image content to NexaData enterprise solutions or answer the user query accurately."
                                    )
                                },
                                {
                                    "role": "user",
                                    "content": [
                                        {"type": "text", "text": prompt_text},
                                        {
                                            "type": "image_url",
                                            "image_url": {
                                                "url": f"data:{attachment['mime_type']};base64,{attachment['b64_image']}"
                                            }
                                        }
                                    ]
                                }
                            ],
                            temperature=0.2,
                            max_tokens=700
                        )
                        reply = response.choices[0].message.content.strip()
                        return ChatResponse(
                            reply=reply,
                            mode="company",
                            sources=attachment_sources,
                            timestamp=self._get_timestamp(),
                            attachment_info=attachment_info
                        )
                    except Exception:
                        pass
                
                # Offline image response
                reply = (
                    f"🖼️ **Temporary Image Received:** `{attachment['filename']}`\n"
                    f"- **Summary:** {attachment.get('summary')}\n\n"
                    f"The image was validated and processed in-memory for this query. It is not saved to the permanent knowledge base.\n\n"
                    f"*(Configure `OPENAI_API_KEY` for live multimodal vision analysis).* "
                )
                return ChatResponse(
                    reply=reply,
                    mode="company",
                    sources=attachment_sources,
                    timestamp=self._get_timestamp(),
                    attachment_info=attachment_info
                )

        # 1. First check if this is a live Database query (Products, Clients, Transactions)
        db_content = query_database_smart(message)
        if db_content:
            sources = [
                SourceCitation(
                    document="PostgreSQL Enterprise Database (Live Records)",
                    page=1,
                    score=0.99,
                    snippet="Live relational query executed on NexaData master schema."
                )
            ] + attachment_sources
            return ChatResponse(
                reply=db_content,
                mode="company",
                sources=sources,
                timestamp=self._get_timestamp(),
                attachment_info=attachment_info
            )

        # 2. Query company PDF documents using RAG
        context_chunks = knowledge_base.retrieve_context(message, top_k=2) if message else []

        sources = list(attachment_sources)
        for c in context_chunks:
            sources.append(SourceCitation(
                document=c["source"],
                page=c["page"],
                score=c["similarity_score"],
                snippet=c["text"][:180] + "..."
            ))

        # Check for dynamic temporal query in company mode
        temporal_reply = self._handle_dynamic_temporal_or_capability(message)
        if temporal_reply and any(k in message.lower() for k in ["date", "year", "cutoff", "real-time", "real time"]):
            return ChatResponse(
                reply=f"{temporal_reply}\n\n*(For general open-ended inquiries, you can also use the General Questions tab).* ",
                mode="company",
                sources=[],
                timestamp=self._get_timestamp(),
                attachment_info=attachment_info
            )

        # If attachment is a document or CSV in Company mode
        if attachment and attachment.get("is_document"):
            user_prompt = message.strip() if message.strip() else f"Analyze this uploaded {attachment['extension'].upper()} document and summarize its relevance to NexaData operations."
            if self.client:
                try:
                    kb_text = "\n\n".join([f"[{c['source']} P{c['page']}]: {c['text']}" for c in context_chunks])
                    full_prompt = (
                        f"TEMPORARY UPLOADED FILE ({attachment['filename']}):\n"
                        f"```\n{attachment.get('text_content', '')[:25000]}\n```\n\n"
                        f"OFFICIAL NEXADATA DOCUMENTS:\n{kb_text}\n\n"
                        f"USER QUERY: {user_prompt}"
                    )
                    response = self.client.chat.completions.create(
                        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    "You are NexaData AI. Answer the user query using the attached temporary document "
                                    "and official NexaData company knowledge. Keep the uploaded file temporary and clearly distinguish it."
                                )
                            },
                            {"role": "user", "content": full_prompt}
                        ],
                        temperature=0.2,
                        max_tokens=700
                    )
                    reply = response.choices[0].message.content.strip()
                    return ChatResponse(
                        reply=reply,
                        mode="company",
                        sources=sources,
                        timestamp=self._get_timestamp(),
                        attachment_info=attachment_info
                    )
                except Exception:
                    pass

            # Offline document / CSV in Company mode
            if attachment.get("extension") == "csv":
                reply = (
                    f"📊 **Temporary CSV Attached:** `{attachment['filename']}`\n\n"
                    f"{attachment.get('text_content', '')}\n\n"
                    f"*(File analyzed in-memory. Not added to permanent company knowledge base).* "
                )
            else:
                reply = (
                    f"📄 **Temporary Document Attached:** `{attachment['filename']}` ({attachment.get('summary')})\n\n"
                    f"**Extracted Text Preview:**\n{attachment.get('text_content', '')[:800]}...\n\n"
                    f"*(Temporary file processed in-memory for this query).* "
                )
            return ChatResponse(
                reply=reply,
                mode="company",
                sources=sources,
                timestamp=self._get_timestamp(),
                attachment_info=attachment_info
            )

        if not context_chunks:
            reply = (
                "I could not find information about that in NexaData's official company documents. "
                "Please switch to the **General Questions** tab for open-ended questions."
            )
            return ChatResponse(
                reply=reply,
                mode="company",
                sources=[],
                timestamp=self._get_timestamp(),
                attachment_info=attachment_info
            )

        # If OpenAI client available, generate grounded natural response
        if self.client:
            try:
                sys_prompt, user_prompt = knowledge_base.build_grounded_prompt(message, context_chunks)
                response = self.client.chat.completions.create(
                    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                    messages=[
                        {"role": "system", "content": sys_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.1,
                    max_tokens=500
                )
                reply = response.choices[0].message.content.strip()
                return ChatResponse(
                    reply=reply,
                    mode="company",
                    sources=sources,
                    timestamp=self._get_timestamp(),
                    attachment_info=attachment_info
                )
            except Exception:
                pass  # Fallback to local grounded text

        # Offline / Local Grounded Answer
        best_chunk = context_chunks[0]
        reply = (
            f"{best_chunk['text']}\n\n"
            f"📄 **Source:** `{best_chunk['source']}` (Page {best_chunk['page']})"
        )
        return ChatResponse(
            reply=reply,
            mode="company",
            sources=sources,
            timestamp=self._get_timestamp(),
            attachment_info=attachment_info
        )

    def _get_dynamic_context(self) -> Dict[str, Any]:
        """Dynamically compute runtime date, year, time, and active model configuration."""
        now = datetime.now()
        configured_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        return {
            "current_date": now.strftime("%A, %B %d, %Y"),
            "current_year": str(now.year),
            "current_time": now.strftime("%I:%M %p"),
            "configured_model": configured_model,
        }

    def _build_general_system_prompt(self) -> str:
        """Construct dynamic system prompt with live runtime temporal context and guidelines."""
        ctx = self._get_dynamic_context()
        return (
            f"You are NexaData AI, a helpful, highly knowledgeable assistant for NexaData Solutions.\n"
            f"TEMPORAL CONTEXT (DYNAMICALLY INJECTED FROM RUNTIME ENVIRONMENT):\n"
            f"- Today's current date is {ctx['current_date']}.\n"
            f"- The current year is {ctx['current_year']}.\n"
            f"- The current local time is {ctx['current_time']}.\n\n"
            f"KNOWLEDGE CUTOFF & REAL-TIME DATA GUIDELINES:\n"
            f"1. Never confuse the current date ({ctx['current_date']}) with your training data cutoff.\n"
            f"2. Your exact pre-training cutoff date for model '{ctx['configured_model']}' is not definitively verified by the runtime environment. If asked about your training cutoff, clearly state that your exact training cutoff date is unknown or unverified rather than inventing a date or claiming an unverified cutoff (e.g., do not claim 'October 2023' unless verified).\n"
            f"3. Do not claim real-time web browsing or internet access merely because you have been provided with today's date. State that live information is available ONLY through NexaData's actual integrations—specifically, the connected live PostgreSQL database (for products, client master records, and transactions) and indexed company documents—and not from general web browsing.\n"
            f"4. You are a versatile general-purpose AI assistant. Answer helpfully, thoroughly, and clearly on any topic, creative task, writing, brainstorming, planning, or general question."
        )

    def _handle_dynamic_temporal_or_capability(self, message: str) -> Optional[str]:
        """Dynamically resolve date, year, cutoff, and real-time questions at runtime without static hardcoding."""
        ctx = self._get_dynamic_context()
        m_lower = message.lower().strip()

        # Dynamic date query
        if any(q in m_lower for q in ["today's date", "todays date", "what is the date", "what date is it", "current date", "today date"]):
            return f"Today's date is **{ctx['current_date']}**."

        # Dynamic year query
        if any(q in m_lower for q in ["what year is it", "current year", "which year", "what year are we in", "what is the year"]):
            return f"The current year is **{ctx['current_year']}**."

        # Dynamic knowledge cutoff query
        if any(q in m_lower for q in ["knowledge cutoff", "training cutoff", "cutoff date", "cut-off", "cut off"]):
            return (
                f"The exact training cutoff date for the configured model (`{ctx['configured_model']}`) "
                f"cannot be definitively verified and is unknown. "
                f"Please note that today's date is **{ctx['current_date']}**, which is provided dynamically by the runtime "
                f"and is distinct from any model training cutoff."
            )

        # Dynamic real-time capabilities query
        if any(q in m_lower for q in ["real-time", "real time", "browse the web", "web access", "internet access", "live information", "access real time"]):
            return (
                f"Live information is available only through NexaData's active data integrations—specifically, "
                f"our connected PostgreSQL database (covering products, client master accounts, and 20 business transactions) "
                f"and indexed official company documents. I do not have unrestricted live web browsing or open internet access. "
                f"Knowledge of today's date (**{ctx['current_date']}**) is provided dynamically by the application runtime."
            )

        return None

    def handle_general_question(self, message: str, attachment: Optional[Dict[str, Any]] = None) -> ChatResponse:
        """Answer general-purpose AI question or direct database query, with vision and document analysis."""
        attachment_sources = []
        attachment_info = None

        if attachment:
            attachment_info = {
                "filename": attachment.get("filename"),
                "summary": attachment.get("summary"),
                "is_image": attachment.get("is_image", False),
                "size_formatted": attachment.get("size_formatted")
            }
            label = "Attached Image" if attachment.get("is_image") else "Attached File"
            attachment_sources.append(SourceCitation(
                document=f"{label}: {attachment.get('filename')}",
                page=1,
                score=1.0,
                snippet=attachment.get("summary", "Uploaded attachment")
            ))

            # 1. Handle Image with Vision Model
            if attachment.get("is_image"):
                prompt_text = message.strip() if message.strip() else "Analyze this image thoroughly. Describe all elements, extract or transcribe any text or data visualizations, and provide key takeaways."
                if self.client:
                    try:
                        response = self.client.chat.completions.create(
                            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                            messages=[
                                {
                                    "role": "system",
                                    "content": (
                                        self._build_general_system_prompt() + 
                                        "\nYou have advanced multimodal vision capabilities. Inspect the provided image in detail, identify objects, interpret charts/data, and answer the user query with structure and clarity."
                                    )
                                },
                                {
                                    "role": "user",
                                    "content": [
                                        {"type": "text", "text": prompt_text},
                                        {
                                            "type": "image_url",
                                            "image_url": {
                                                "url": f"data:{attachment['mime_type']};base64,{attachment['b64_image']}"
                                            }
                                        }
                                    ]
                                }
                            ],
                            temperature=0.3,
                            max_tokens=800
                        )
                        reply = response.choices[0].message.content.strip()
                        return ChatResponse(
                            reply=reply,
                            mode="general",
                            sources=attachment_sources,
                            timestamp=self._get_timestamp(),
                            attachment_info=attachment_info
                        )
                    except Exception:
                        pass
                
                # Offline image response
                reply = (
                    f"🖼️ **Image Analyzed:** `{attachment['filename']}`\n\n"
                    f"- **Summary:** {attachment.get('summary')}\n"
                    f"- **Dimensions:** {attachment.get('metadata', {}).get('width')} x {attachment.get('metadata', {}).get('height')} px\n"
                    f"- **Size:** {attachment.get('size_formatted')}\n\n"
                    f"The image was validated and verified in memory. "
                    f"*(Configure `OPENAI_API_KEY` in `.env` to enable live multimodal vision reasoning).* "
                )
                return ChatResponse(
                    reply=reply,
                    mode="general",
                    sources=attachment_sources,
                    timestamp=self._get_timestamp(),
                    attachment_info=attachment_info
                )

            # 2. Handle Document / CSV / Data in General Mode
            if attachment.get("is_document"):
                user_prompt = message.strip() if message.strip() else f"Analyze this {attachment['extension'].upper()} file, summarize its contents, and provide key insights and takeaways."
                if self.client:
                    try:
                        doc_text = attachment.get("text_content", "")[:35000]
                        full_prompt = (
                            f"ATTACHED FILE: {attachment['filename']} ({attachment.get('summary')})\n"
                            f"CONTENT:\n```\n{doc_text}\n```\n\n"
                            f"USER INSTRUCTION: {user_prompt}"
                        )
                        response = self.client.chat.completions.create(
                            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                            messages=[
                                {
                                    "role": "system",
                                    "content": (
                                        self._build_general_system_prompt() + 
                                        "\nYou are analyzing a user-uploaded file. Provide accurate, well-structured summaries and data insights."
                                    )
                                },
                                {"role": "user", "content": full_prompt}
                            ],
                            temperature=0.2,
                            max_tokens=800
                        )
                        reply = response.choices[0].message.content.strip()
                        return ChatResponse(
                            reply=reply,
                            mode="general",
                            sources=attachment_sources,
                            timestamp=self._get_timestamp(),
                            attachment_info=attachment_info
                        )
                    except Exception:
                        pass

                # Offline Document / CSV response
                if attachment.get("extension") == "csv":
                    reply = (
                        f"📊 **CSV Data Analysis for `{attachment['filename']}`**\n\n"
                        f"{attachment.get('text_content', '')}\n\n"
                        f"*(Analyzed in-memory using Pandas. Configure `OPENAI_API_KEY` for live generative data exploration).* "
                    )
                else:
                    reply = (
                        f"📄 **Document Summary for `{attachment['filename']}`** ({attachment.get('summary')})\n\n"
                        f"**Text Content:**\n\n{attachment.get('text_content', '')[:1200]}...\n\n"
                        f"*(Extracted in-memory. Configure `OPENAI_API_KEY` for interactive conversational Q&A).* "
                    )
                return ChatResponse(
                    reply=reply,
                    mode="general",
                    sources=attachment_sources,
                    timestamp=self._get_timestamp(),
                    attachment_info=attachment_info
                )

        # 1. Check for database query
        db_content = query_database_smart(message)
        if db_content and any(k in message.lower() for k in ["database", "transaction", "client master", "product"]):
            return ChatResponse(
                reply=db_content,
                mode="general",
                sources=[],
                timestamp=self._get_timestamp(),
                attachment_info=attachment_info
            )

        # 2. Check for dynamic temporal / capability query (deterministic resolution)
        temporal_reply = self._handle_dynamic_temporal_or_capability(message)
        if temporal_reply:
            return ChatResponse(
                reply=temporal_reply,
                mode="general",
                sources=[],
                timestamp=self._get_timestamp(),
                attachment_info=attachment_info
            )

        # 3. If OpenAI client available, invoke with dynamic temporal system prompt
        if self.client:
            try:
                sys_prompt = self._build_general_system_prompt()
                response = self.client.chat.completions.create(
                    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                    messages=[
                        {
                            "role": "system",
                            "content": sys_prompt
                        },
                        {"role": "user", "content": message}
                    ],
                    temperature=0.7,
                    max_tokens=600
                )
                reply = response.choices[0].message.content.strip()
                return ChatResponse(
                    reply=reply,
                    mode="general",
                    sources=[],
                    timestamp=self._get_timestamp(),
                    attachment_info=attachment_info
                )
            except Exception:
                pass

        # 4. Dynamic Offline General AI Answer
        ctx = self._get_dynamic_context()
        reply = (
            f"Hello! In **General Questions** mode, I am a versatile general-purpose AI assistant "
            f"ready to help with any topic, idea, writing, research, or question.\n\n"
            f"*(Current date: {ctx['current_date']}. To enable cloud LLM generative completions, "
            f"configure your server OPENAI_API_KEY in `.env`).*"
        )
        return ChatResponse(
            reply=reply,
            mode="general",
            sources=[],
            timestamp=self._get_timestamp(),
            attachment_info=attachment_info
        )

    def process_message(self, message: str, mode: str = "company", attachment: Optional[Dict[str, Any]] = None) -> ChatResponse:
        """Route message based on selected tab mode with optional temporary attachment."""
        if mode == "company":
            return self.handle_company_question(message, attachment=attachment)
        else:
            return self.handle_general_question(message, attachment=attachment)

# Global orchestrator
orchestrator = ChatOrchestrator()
