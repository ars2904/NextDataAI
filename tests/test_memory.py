"""Unit tests for Phase 1: Multi-Turn Conversational Memory & Context-Aware Follow-ups."""
import sys
import unittest
from pathlib import Path
from fastapi.testclient import TestClient

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.main import app
from backend.models import ChatRequest, ConversationMessage
from backend.orchestrator import orchestrator

client = TestClient(app)

class TestConversationalMemory(unittest.TestCase):
    """Test suite for conversation history preservation and context-aware follow-up reasoning."""

    def test_chat_request_with_history_schema(self):
        """Verify ChatRequest correctly parses conversation_history."""
        req = ChatRequest(
            message="How much does it cost?",
            mode="company",
            conversation_history=[
                ConversationMessage(role="user", content="What is NexaData Enterprise Platform?"),
                ConversationMessage(role="assistant", content="NexaData Enterprise is an autonomous analytics platform.")
            ]
        )
        self.assertEqual(len(req.conversation_history), 2)
        self.assertEqual(req.conversation_history[0].role, "user")
        self.assertEqual(req.conversation_history[1].role, "assistant")

    def test_query_expansion_with_history(self):
        """Verify short follow-up questions are expanded with subject context from previous turn."""
        history = [
            ConversationMessage(role="user", content="What is NexaData Enterprise Platform?"),
            ConversationMessage(role="assistant", content="NexaData Enterprise includes autonomous data ingestion and modeling.")
        ]
        expanded = orchestrator._expand_query_with_history("How much does it cost?", history)
        self.assertIn("NexaData Enterprise Platform", expanded)
        self.assertIn("How much does it cost?", expanded)

    def test_query_expansion_preserves_standalone_queries(self):
        """Verify standalone long queries without pronouns are preserved as-is."""
        history = [
            ConversationMessage(role="user", content="What is NexaData?"),
            ConversationMessage(role="assistant", content="An autonomous analytics engine.")
        ]
        standalone_query = "Describe the PostgreSQL relational architecture and data models."
        expanded = orchestrator._expand_query_with_history(standalone_query, history)
        self.assertEqual(expanded, standalone_query)

    def test_history_message_formatting(self):
        """Verify _format_history_messages properly creates OpenAI-compatible message list."""
        history = [
            ConversationMessage(role="user", content="First question"),
            ConversationMessage(role="assistant", content="First reply"),
            {"role": "user", "content": "Second question"}
        ]
        formatted = orchestrator._format_history_messages(history)
        self.assertEqual(len(formatted), 3)
        self.assertEqual(formatted[0]["role"], "user")
        self.assertEqual(formatted[0]["content"], "First question")
        self.assertEqual(formatted[1]["role"], "assistant")
        self.assertEqual(formatted[2]["role"], "user")

    def test_api_chat_endpoint_with_history_general_mode(self):
        """Verify /api/chat endpoint accepts history and returns valid response in general mode."""
        payload = {
            "message": "Can you summarize what we just discussed?",
            "mode": "general",
            "conversation_history": [
                {"role": "user", "content": "What is data science?"},
                {"role": "assistant", "content": "Data science combines domain expertise, programming, and statistics."}
            ]
        }
        res = client.post("/api/chat", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["mode"], "general")
        self.assertTrue(len(data["reply"]) > 0)
        self.assertIn("timestamp", data)

    def test_api_chat_endpoint_with_history_company_mode(self):
        """Verify /api/chat endpoint in company mode resolves follow-up queries with history."""
        payload = {
            "message": "What are its key features?",
            "mode": "company",
            "conversation_history": [
                {"role": "user", "content": "What is NexaData and what are its solutions?"},
                {"role": "assistant", "content": "NexaData provides autonomous intelligence pipelines."}
            ]
        }
        res = client.post("/api/chat", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["mode"], "company")
        self.assertTrue(len(data["reply"]) > 0)

    def test_api_chat_upload_with_history(self):
        """Verify /api/chat-upload multipart endpoint parses serialized conversation_history."""
        import json
        history_json = json.dumps([
            {"role": "user", "content": "What is the return policy?"},
            {"role": "assistant", "content": "14-day 100% money-back satisfaction guarantee."}
        ])
        res = client.post(
            "/api/chat-upload",
            data={
                "message": "Does that apply to all enterprise plans?",
                "mode": "company",
                "conversation_history": history_json
            }
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["mode"], "company")
        self.assertTrue(len(data["reply"]) > 0)

if __name__ == "__main__":
    unittest.main()
