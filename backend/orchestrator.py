"""Chat Orchestrator for Dual-Mode Conversation."""
import os
import re
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from rag.engine import knowledge_base
from backend.models import SourceCitation, ChatResponse
from database.postgres import query_database_smart
from database.sql_engine import answer_business_data_query

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

    def _format_history_messages(self, conversation_history: Optional[List[Any]]) -> List[Dict[str, str]]:
        """Extract and format recent conversation messages into OpenAI message dictionaries."""
        formatted = []
        if not conversation_history:
            return formatted
        for item in conversation_history[-8:]:
            role = getattr(item, "role", None) or (item.get("role") if isinstance(item, dict) else "user")
            content = getattr(item, "content", None) or (item.get("content") if isinstance(item, dict) else "")
            if role in ("user", "assistant") and content:
                formatted.append({"role": role, "content": str(content).strip()})
        return formatted

    def _expand_query_with_history(self, message: str, conversation_history: Optional[List[Any]]) -> str:
        """Expand short follow-up questions with subject context from previous conversation turns."""
        msg = message.strip()
        if not conversation_history or not msg:
            return msg

        # Tokenize query words to prevent substring false positives
        words = msg.split()
        tokens = set(re.findall(r'\b[a-zA-Z]+\b', msg.lower()))
        pronouns = {"it", "its", "they", "them", "their", "this", "that", "these", "those"}
        follow_up_cues = {
            "cost", "price", "pricing", "features", "details", "specifications",
            "who", "why", "when", "where", "how"
        }

        # If sentence is long (8+ words) and contains no reference pronouns, it is standalone
        if len(words) >= 8 and not tokens.intersection(pronouns):
            return msg

        # For shorter queries, check if it contains pronouns or follow-up cues or is very short
        is_follow_up = len(words) <= 5 or bool(tokens.intersection(pronouns)) or bool(tokens.intersection(follow_up_cues))
        if not is_follow_up:
            return msg

        recent_user_turn = None
        for item in reversed(conversation_history):
            role = getattr(item, "role", None) or (item.get("role") if isinstance(item, dict) else "")
            content = getattr(item, "content", None) or (item.get("content") if isinstance(item, dict) else "")
            if role == "user" and content and content.strip() != msg:
                recent_user_turn = content.strip()
                break

        if recent_user_turn:
            return f"{recent_user_turn} {msg}"
        return msg

    def handle_company_question(
        self,
        message: str,
        attachment: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Any]] = None
    ) -> ChatResponse:
        """Query company PDF documents using RAG or direct database records, with optional temporary attachment and multi-turn context."""
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
                        history_msgs = self._format_history_messages(conversation_history)
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
                                *history_msgs,
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

        # Context-aware query expansion for follow-up questions
        effective_query = self._expand_query_with_history(message, conversation_history)

        # 1. First check if this is a live Database query (Products, Clients, Transactions)
        db_content = query_database_smart(message)
        if not db_content and effective_query != message:
            db_content = query_database_smart(effective_query)

        # If not matched by static patterns, check dynamic Text-to-SQL Analytics engine
        if not db_content:
            sql_reply = answer_business_data_query(effective_query, client=self.client)
            if not sql_reply and effective_query != message:
                sql_reply = answer_business_data_query(message, client=self.client)
            if sql_reply:
                db_content = sql_reply

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

        # 2. Query company PDF documents using RAG with expanded retrieval query
        context_chunks = knowledge_base.retrieve_context(effective_query, top_k=2) if effective_query else []
        if not context_chunks and message and effective_query != message:
            context_chunks = knowledge_base.retrieve_context(message, top_k=2)

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
                    history_msgs = self._format_history_messages(conversation_history)
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
                            *history_msgs,
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
                history_msgs = self._format_history_messages(conversation_history)
                messages = (
                    [{"role": "system", "content": sys_prompt}]
                    + history_msgs
                    + [{"role": "user", "content": user_prompt}]
                )
                response = self.client.chat.completions.create(
                    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                    messages=messages,
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

    def handle_general_question(
        self,
        message: str,
        attachment: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Any]] = None
    ) -> ChatResponse:
        """Answer general-purpose AI question or direct database query, with vision, document analysis, and multi-turn context."""
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
                        history_msgs = self._format_history_messages(conversation_history)
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
                                *history_msgs,
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
                        history_msgs = self._format_history_messages(conversation_history)
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
                                *history_msgs,
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

        # 1. Check for database query (with query expansion for follow-up turns)
        effective_query = self._expand_query_with_history(message, conversation_history)
        db_content = query_database_smart(message)
        if not db_content and effective_query != message:
            db_content = query_database_smart(effective_query)

        # Check dynamic Text-to-SQL Analytics engine
        sql_content = None
        if not db_content:
            sql_content = answer_business_data_query(effective_query, client=self.client)
            if not sql_content and effective_query != message:
                sql_content = answer_business_data_query(message, client=self.client)
            if sql_content:
                db_content = sql_content

        combined_check = (message + " " + effective_query).lower()
        if db_content and (sql_content or any(k in combined_check for k in ["database", "transaction", "client master", "product", "customer", "order", "inventory", "department"])):
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

        # 3. If OpenAI client available, invoke with dynamic temporal system prompt and conversation history
        if self.client:
            try:
                sys_prompt = self._build_general_system_prompt()
                history_msgs = self._format_history_messages(conversation_history)
                messages = (
                    [{"role": "system", "content": sys_prompt}]
                    + history_msgs
                    + [{"role": "user", "content": message}]
                )
                response = self.client.chat.completions.create(
                    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                    messages=messages,
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
        if conversation_history:
            reply = (
                f"Continuing our conversation on **'{message}'**:\n\n"
                f"I acknowledge your follow-up context. In offline mode without an active cloud LLM key, "
                f"detailed generative continuation is limited. You can query official company documents "
                f"and database records in **Company Questions** mode, or configure `OPENAI_API_KEY` for live generative responses."
            )
        else:
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

    def process_message(
        self,
        message: str,
        mode: str = "company",
        attachment: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Any]] = None
    ) -> ChatResponse:
        """Route message based on selected tab mode with optional temporary attachment and conversation history."""
        if mode == "company":
            return self.handle_company_question(message, attachment=attachment, conversation_history=conversation_history)
        else:
            return self.handle_general_question(message, attachment=attachment, conversation_history=conversation_history)

    def stream_message(
        self,
        message: str,
        mode: str = "company",
        attachment: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Any]] = None
    ):
        """
        Progressive token streaming generator using Server-Sent Events (SSE).
        Yields `data: {"token": "..."}\n\n` for progressive typewriter rendering,
        and terminates with `data: {"done": true, "reply": "...", "sources": [...], ...}\n\n`.
        """
        try:
            # Check for live OpenAI client and no attachments
            if self.client and not attachment:
                effective_query = self._expand_query_with_history(message, conversation_history)

                # 1. Company Mode
                if mode == "company":
                    # Check for direct database or temporal matches first
                    db_content = query_database_smart(message)
                    if not db_content and effective_query != message:
                        db_content = query_database_smart(effective_query)
                    if not db_content:
                        sql_reply = answer_business_data_query(effective_query, client=self.client)
                        if not sql_reply and effective_query != message:
                            sql_reply = answer_business_data_query(message, client=self.client)
                        if sql_reply:
                            db_content = sql_reply

                    if db_content:
                        words = re.findall(r'\S+|\s+', db_content)
                        for w in words:
                            yield f"data: {json.dumps({'token': w})}\n\n"
                        sources = [{"document": "PostgreSQL Enterprise Database (Live Records)", "page": 1, "score": 0.99, "snippet": "Live relational query executed on NexaData master schema."}]
                        yield f"data: {json.dumps({'done': True, 'mode': 'company', 'reply': db_content, 'sources': sources, 'timestamp': self._get_timestamp()})}\n\n"
                        return

                    temporal_reply = self._handle_dynamic_temporal_or_capability(message)
                    if temporal_reply and any(k in message.lower() for k in ["date", "year", "cutoff", "real-time", "real time"]):
                        reply = f"{temporal_reply}\n\n*(For general open-ended inquiries, you can also use the General Questions tab).* "
                        words = re.findall(r'\S+|\s+', reply)
                        for w in words:
                            yield f"data: {json.dumps({'token': w})}\n\n"
                        yield f"data: {json.dumps({'done': True, 'mode': 'company', 'reply': reply, 'sources': [], 'timestamp': self._get_timestamp()})}\n\n"
                        return

                    context_chunks = knowledge_base.retrieve_context(effective_query, top_k=2) if effective_query else []
                    if not context_chunks and message and effective_query != message:
                        context_chunks = knowledge_base.retrieve_context(message, top_k=2)

                    if not context_chunks:
                        reply = "I could not find information about that in NexaData's official company documents. Please switch to the **General Questions** tab for open-ended questions."
                        words = re.findall(r'\S+|\s+', reply)
                        for w in words:
                            yield f"data: {json.dumps({'token': w})}\n\n"
                        yield f"data: {json.dumps({'done': True, 'mode': 'company', 'reply': reply, 'sources': [], 'timestamp': self._get_timestamp()})}\n\n"
                        return

                    # Live LLM Streaming
                    sys_prompt, user_prompt = knowledge_base.build_grounded_prompt(message, context_chunks)
                    history_msgs = self._format_history_messages(conversation_history)
                    messages = [{"role": "system", "content": sys_prompt}] + history_msgs + [{"role": "user", "content": user_prompt}]
                    stream = self.client.chat.completions.create(
                        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                        messages=messages,
                        temperature=0.1,
                        max_tokens=500,
                        stream=True
                    )
                    full_reply = []
                    for chunk in stream:
                        delta = chunk.choices[0].delta.content if chunk.choices and chunk.choices[0].delta else ""
                        if delta:
                            full_reply.append(delta)
                            yield f"data: {json.dumps({'token': delta})}\n\n"

                    complete_reply = "".join(full_reply).strip()
                    sources = [
                        {
                            "document": c["source"],
                            "page": c["page"],
                            "score": c["similarity_score"],
                            "snippet": c["text"][:180] + "..."
                        }
                        for c in context_chunks
                    ]
                    yield f"data: {json.dumps({'done': True, 'mode': 'company', 'reply': complete_reply, 'sources': sources, 'timestamp': self._get_timestamp()})}\n\n"
                    return

                # 2. General Mode
                else:
                    db_content = query_database_smart(message)
                    if not db_content and effective_query != message:
                        db_content = query_database_smart(effective_query)
                    sql_content = None
                    if not db_content:
                        sql_content = answer_business_data_query(effective_query, client=self.client)
                        if not sql_content and effective_query != message:
                            sql_content = answer_business_data_query(message, client=self.client)
                        if sql_content:
                            db_content = sql_content

                    combined_check = (message + " " + effective_query).lower()
                    if db_content and (sql_content or any(k in combined_check for k in ["database", "transaction", "client master", "product", "customer", "order", "inventory", "department"])):
                        words = re.findall(r'\S+|\s+', db_content)
                        for w in words:
                            yield f"data: {json.dumps({'token': w})}\n\n"
                        yield f"data: {json.dumps({'done': True, 'mode': 'general', 'reply': db_content, 'sources': [], 'timestamp': self._get_timestamp()})}\n\n"
                        return

                    temporal_reply = self._handle_dynamic_temporal_or_capability(message)
                    if temporal_reply:
                        words = re.findall(r'\S+|\s+', temporal_reply)
                        for w in words:
                            yield f"data: {json.dumps({'token': w})}\n\n"
                        yield f"data: {json.dumps({'done': True, 'mode': 'general', 'reply': temporal_reply, 'sources': [], 'timestamp': self._get_timestamp()})}\n\n"
                        return

                    sys_prompt = self._build_general_system_prompt()
                    history_msgs = self._format_history_messages(conversation_history)
                    messages = [{"role": "system", "content": sys_prompt}] + history_msgs + [{"role": "user", "content": message}]
                    stream = self.client.chat.completions.create(
                        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                        messages=messages,
                        temperature=0.7,
                        max_tokens=600,
                        stream=True
                    )
                    full_reply = []
                    for chunk in stream:
                        delta = chunk.choices[0].delta.content if chunk.choices and chunk.choices[0].delta else ""
                        if delta:
                            full_reply.append(delta)
                            yield f"data: {json.dumps({'token': delta})}\n\n"

                    complete_reply = "".join(full_reply).strip()
                    yield f"data: {json.dumps({'done': True, 'mode': 'general', 'reply': complete_reply, 'sources': [], 'timestamp': self._get_timestamp()})}\n\n"
                    return

            # Fallback for attachments, offline responses, or non-streamable paths
            resp = self.process_message(
                message=message,
                mode=mode,
                attachment=attachment,
                conversation_history=conversation_history
            )
            words = re.findall(r'\S+|\s+', resp.reply)
            for w in words:
                yield f"data: {json.dumps({'token': w})}\n\n"

            sources = [s.model_dump() if hasattr(s, "model_dump") else (s.dict() if hasattr(s, "dict") else s) for s in resp.sources]
            yield f"data: {json.dumps({'done': True, 'mode': resp.mode, 'reply': resp.reply, 'sources': sources, 'timestamp': resp.timestamp, 'attachment_info': resp.attachment_info})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"

# Global orchestrator
orchestrator = ChatOrchestrator()
