"""Chat Orchestrator for Dual-Mode Conversation."""
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from rag.engine import knowledge_base
from backend.models import SourceCitation, ChatResponse

load_dotenv()

class ChatOrchestrator:
    """
    Coordinates between General Model and Company PDF RAG Engine.
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

    def handle_company_question(self, message: str) -> ChatResponse:
        """Query company PDF documents using RAG."""
        context_chunks = knowledge_base.retrieve_context(message, top_k=2)

        sources = []
        for c in context_chunks:
            sources.append(SourceCitation(
                document=c["source"],
                page=c["page"],
                score=c["similarity_score"],
                snippet=c["text"][:180] + "..."
            ))

        if not context_chunks:
            reply = (
                "I could not find information about that in NexaData's official company documents. "
                "Please switch to the **General Questions** tab for open-ended questions."
            )
            return ChatResponse(
                reply=reply,
                mode="company",
                sources=[],
                timestamp=self._get_timestamp()
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
                    timestamp=self._get_timestamp()
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
            timestamp=self._get_timestamp()
        )

    def handle_general_question(self, message: str) -> ChatResponse:
        """Answer general-purpose AI question."""
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are NexaData AI, a helpful, intelligent assistant. "
                                "Answer clearly, accurately, and politely on Python, data science, "
                                "analytics, and general knowledge."
                            )
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
                    timestamp=self._get_timestamp()
                )
            except Exception:
                pass

        # Offline General AI Answer
        reply = (
            f"Hello! In **General Questions** mode, I can help answer general topics, definitions, "
            f"and broad programming/data science questions.\n\n"
            f"*(Note: You asked: '{message}'. To connect this to live cloud LLM completions, "
            f"ensure your server OPENAI_API_KEY is configured in .env. Switch to 'Company Questions' "
            f"to query NexaData's local PDF documents directly).* "
        )
        return ChatResponse(
            reply=reply,
            mode="general",
            sources=[],
            timestamp=self._get_timestamp()
        )

    def process_message(self, message: str, mode: str = "company") -> ChatResponse:
        """Route message based on selected tab mode."""
        if mode == "company":
            return self.handle_company_question(message)
        else:
            return self.handle_general_question(message)

# Global orchestrator
orchestrator = ChatOrchestrator()
