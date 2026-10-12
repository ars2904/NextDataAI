"""Unit and integration tests for VedaNova RAG Knowledge Base."""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from rag.engine import VedaNovaKnowledgeBase, DOCS_DIR

def test_knowledge_base_indexing():
    """Verify company PDF document loading and vector indexing."""
    kb = VedaNovaKnowledgeBase(DOCS_DIR)
    assert len(kb.pages) > 0, "No pages extracted from company documents"
    assert len(kb.chunks) > 0, "No chunks generated"
    assert any("NexaData" in f for f in kb.indexed_files)

def test_semantic_retrieval():
    """Verify semantic context retrieval accuracy and relevance."""
    kb = VedaNovaKnowledgeBase(DOCS_DIR)
    
    # Test service query
    services_res = kb.retrieve_context("wellness services and pricing", top_k=2)
    assert len(services_res) > 0
    assert services_res[0]["similarity_score"] > 0
    
    # Test policy query
    policy_res = kb.retrieve_context("cancellation and refund policy", top_k=2)
    assert len(policy_res) > 0
    assert any("cancellation" in r["text"].lower() or "refund" in r["text"].lower() for r in policy_res)

def test_grounded_prompt_construction():
    """Verify strict anti-hallucination prompt formatting."""
    kb = VedaNovaKnowledgeBase(DOCS_DIR)
    sample_context = kb.retrieve_context("refund policy", top_k=1)
    sys_prompt, user_content = kb.build_grounded_prompt("What is the refund policy?", sample_context)
    
    assert "STRICTLY grounded" in sys_prompt
    assert "OFFICIAL COMPANY CONTEXT" in user_content

if __name__ == "__main__":
    test_knowledge_base_indexing()
    test_semantic_retrieval()
    test_grounded_prompt_construction()
    print("All RAG unit tests passed successfully.")
