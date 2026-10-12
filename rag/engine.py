"""RAG Engine: Knowledge Base Orchestrator for VedaNova AI."""
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from rag.pdf_loader import load_all_company_docs
from rag.chunker import chunk_document_pages
from rag.retriever import LocalVectorRetriever

DOCS_DIR = Path(__file__).resolve().parent.parent / "company_docs"

class VedaNovaKnowledgeBase:
    """
    Manages VedaNova's pre-indexed PDF company documents,
    retrieval pipelines, and grounding prompts.
    """
    def __init__(self, docs_dir: Path = DOCS_DIR):
        self.docs_dir = docs_dir
        self.pages = []
        self.chunks = []
        self.retriever = None
        self.indexed_files = []
        self.initialize()

    def initialize(self):
        """Load and index all company PDFs."""
        self.pages = load_all_company_docs(self.docs_dir)
        self.chunks = chunk_document_pages(self.pages, chunk_size=300, chunk_overlap=60)
        self.retriever = LocalVectorRetriever(self.chunks)
        self.indexed_files = list(set(p["source"] for p in self.pages))

    def retrieve_context(self, question: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieve the most relevant passages for a question."""
        if not self.retriever or not self.chunks:
            return []
        return self.retriever.search(question, top_k=top_k)

    def build_grounded_prompt(self, question: str, context_chunks: List[Dict[str, Any]]) -> Tuple[str, str]:
        """
        Create a strictly grounded system prompt and user context string.
        """
        sources_text = []
        for idx, chunk in enumerate(context_chunks, 1):
            sources_text.append(
                f"[Document: {chunk['source']}, Page {chunk['page']}]\n{chunk['text']}"
            )

        context_block = "\n\n".join(sources_text)

        system_prompt = (
            "You are NexaData AI, the official intelligent assistant for NexaData Solutions.\n"
            "Your answers in Company Questions mode must be STRICTLY grounded in the provided company documents.\n"
            "RULES:\n"
            "1. Answer ONLY using information explicitly mentioned in the context below.\n"
            "2. If the answer is not mentioned in the context, reply: 'I can only answer questions covered in NexaData's official company documents. For general topics, please switch to the General Questions tab.'\n"
            "3. Be polite, professional, and clear.\n"
            "4. Cite the source document and page number at the end of your answer (e.g., 'Source: NexaData_Company_Overview_and_Services.pdf, Page 1')."
        )

        user_content = f"OFFICIAL COMPANY CONTEXT:\n{context_block}\n\nUSER QUESTION:\n{question}"
        return system_prompt, user_content

    def answer_company_question_offline(self, question: str, context_chunks: List[Dict[str, Any]]) -> str:
        """
        Deterministic, offline extraction fallback when no LLM API key is present.
        """
        if not context_chunks:
            return (
                "I could not find relevant information in NexaData's official company documents. "
                "Please switch to the General Questions tab for general inquiries."
            )

        best_chunk = context_chunks[0]
        return (
            f"{best_chunk['text']}\n\n"
            f"📄 *Source: {best_chunk['source']} (Page {best_chunk['page']})*"
        )

# Global singleton instance
knowledge_base = VedaNovaKnowledgeBase()
