"""Unit tests for Phase 4 (PostgreSQL Chat Persistence) & Phase 5 (Rate Limiting & Security Guardrails)."""
import sys
import unittest
from pathlib import Path
from fastapi.testclient import TestClient

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.main import app, RATE_LIMIT_BUCKETS

client = TestClient(app)

class TestPersistenceAndSecurity(unittest.TestCase):
    """Test suite for server-side conversation persistence and security rate limiting."""

    def setUp(self):
        # Clear rate limit buckets for clean test isolation
        RATE_LIMIT_BUCKETS.clear()

    def test_save_and_retrieve_conversation(self):
        """Verify saving a conversation session with messages and fetching it back."""
        test_session_id = "test_conv_sync_123"
        payload = {
            "id": test_session_id,
            "title": "Quarterly Revenue Discussion",
            "mode": "company",
            "messages": [
                {"role": "user", "text": "What is our total revenue?"},
                {"role": "assistant", "reply": "Total recognized revenue is over $1M USD."}
            ]
        }

        # 1. Save
        res = client.post("/api/conversations", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "saved")

        # 2. List
        list_res = client.get("/api/conversations")
        self.assertEqual(list_res.status_code, 200)
        convs = list_res.json()["conversations"]
        self.assertTrue(any(c["session_id"] == test_session_id for c in convs))

        # 3. Get messages
        msg_res = client.get(f"/api/conversations/{test_session_id}")
        self.assertEqual(msg_res.status_code, 200)
        msgs = msg_res.json()["messages"]
        self.assertEqual(len(msgs), 2)
        self.assertEqual(msgs[0]["role"], "user")
        self.assertIn("What is our total revenue?", msgs[0]["text"])

        # 4. Delete
        del_res = client.delete(f"/api/conversations/{test_session_id}")
        self.assertEqual(del_res.status_code, 200)
        self.assertEqual(del_res.json()["status"], "deleted")

    def test_rate_limiting_guardrail(self):
        """Verify rate limiter blocks runaway requests when threshold is exceeded."""
        endpoint = "/api/chat"
        # Rule for /api/chat is 60 requests/minute
        # Simulate bucket filling
        key = "testclient:/api/chat"
        import time
        now = time.time()
        RATE_LIMIT_BUCKETS[key] = [now] * 60  # fill bucket to capacity

        res = client.post(endpoint, json={"message": "ping", "mode": "company"})
        self.assertEqual(res.status_code, 429)
        self.assertIn("Rate limit exceeded", res.json()["detail"])

        # Clear bucket and verify it recovers
        RATE_LIMIT_BUCKETS.clear()
        res_ok = client.post(endpoint, json={"message": "What is today's date?", "mode": "company"})
        self.assertEqual(res_ok.status_code, 200)

if __name__ == "__main__":
    unittest.main()
