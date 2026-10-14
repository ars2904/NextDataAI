"""Unit tests for Phase 3: Real-Time Token Streaming (Server-Sent Events / SSE)."""
import sys
import json
import unittest
from pathlib import Path
from fastapi.testclient import TestClient

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.main import app

client = TestClient(app)

class TestStreamingEndpoint(unittest.TestCase):
    """Test suite for SSE token streaming endpoint and progressive rendering."""

    def test_streaming_endpoint_general_mode(self):
        """Verify /api/chat-stream returns text/event-stream and yields progressive tokens."""
        with client.stream(
            "POST",
            "/api/chat-stream",
            json={"message": "What is machine learning?", "mode": "general"}
        ) as response:
            self.assertEqual(response.status_code, 200)
            self.assertIn("text/event-stream", response.headers.get("content-type", ""))

            tokens_received = []
            done_payload = None

            for line in response.iter_lines():
                if line.startswith("data:"):
                    json_str = line[5:].strip()
                    if json_str:
                        data = json.loads(json_str)
                        if "token" in data:
                            tokens_received.append(data["token"])
                        if data.get("done"):
                            done_payload = data

            self.assertGreater(len(tokens_received), 0, "Expected at least one token chunk streamed.")
            self.assertIsNotNone(done_payload, "Expected terminal done event in SSE stream.")
            self.assertEqual(done_payload["mode"], "general")
            self.assertIn("timestamp", done_payload)

    def test_streaming_endpoint_company_mode(self):
        """Verify /api/chat-stream in company mode streams grounded RAG or database reply."""
        with client.stream(
            "POST",
            "/api/chat-stream",
            json={"message": "What is your total revenue summary?", "mode": "company"}
        ) as response:
            self.assertEqual(response.status_code, 200)
            self.assertIn("text/event-stream", response.headers.get("content-type", ""))

            tokens_received = []
            done_payload = None

            for line in response.iter_lines():
                if line.startswith("data:"):
                    json_str = line[5:].strip()
                    if json_str:
                        data = json.loads(json_str)
                        if "token" in data:
                            tokens_received.append(data["token"])
                        if data.get("done"):
                            done_payload = data

            self.assertGreater(len(tokens_received), 0)
            self.assertIsNotNone(done_payload)
            self.assertEqual(done_payload["mode"], "company")
            self.assertTrue(len(done_payload.get("sources", [])) > 0)

    def test_streaming_endpoint_with_conversation_history(self):
        """Verify /api/chat-stream handles conversation_history seamlessly."""
        with client.stream(
            "POST",
            "/api/chat-stream",
            json={
                "message": "What are its key benefits?",
                "mode": "company",
                "conversation_history": [
                    {"role": "user", "content": "What is NexaData Enterprise Platform?"},
                    {"role": "assistant", "content": "NexaData Enterprise is an autonomous analytics engine."}
                ]
            }
        ) as response:
            self.assertEqual(response.status_code, 200)
            tokens_received = []
            for line in response.iter_lines():
                if line.startswith("data:"):
                    json_str = line[5:].strip()
                    if json_str:
                        data = json.loads(json_str)
                        if "token" in data:
                            tokens_received.append(data["token"])
            self.assertGreater(len(tokens_received), 0)

if __name__ == "__main__":
    unittest.main()
