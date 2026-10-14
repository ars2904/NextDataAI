"""Unit Tests for NexaData AI Phase 6 Authentication & User Isolation."""
import unittest
import uuid
from fastapi.testclient import TestClient
from backend.main import app
from backend.security import hash_password, verify_password, create_access_token, decode_access_token
from database.postgres import db_engine, User, ChatSession

class TestAuthentication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        # Ensure database tables exist
        db_engine.init_database()

    def test_01_password_hashing(self):
        """Test bcrypt hashing and verification."""
        pwd = "SecurePassword2026!"
        hashed = hash_password(pwd)
        self.assertNotEqual(pwd, hashed)
        self.assertTrue(verify_password(pwd, hashed))
        self.assertFalse(verify_password("WrongPassword", hashed))

    def test_02_jwt_token_generation_and_decode(self):
        """Test JWT token encoding and payload decoding."""
        payload = {"sub": "usr_test123", "email": "test@example.com", "role": "user"}
        token = create_access_token(payload)
        self.assertIsInstance(token, str)
        decoded = decode_access_token(token)
        self.assertIsNotNone(decoded)
        self.assertEqual(decoded["sub"], "usr_test123")
        self.assertEqual(decoded["email"], "test@example.com")

    def test_03_default_seeded_accounts_login(self):
        """Test login with default pre-seeded admin and demo accounts."""
        # Demo user login
        res_demo = self.client.post("/api/auth/login", json={
            "email": "demo@nexadata.ai",
            "password": "NexaDemo2026!"
        })
        self.assertEqual(res_demo.status_code, 200)
        data_demo = res_demo.json()
        self.assertIn("access_token", data_demo)
        self.assertEqual(data_demo["user"]["email"], "demo@nexadata.ai")
        self.assertEqual(data_demo["user"]["role"], "user")

        # Admin user login
        res_admin = self.client.post("/api/auth/login", json={
            "email": "admin@nexadata.ai",
            "password": "NexaData2026!"
        })
        self.assertEqual(res_admin.status_code, 200)
        data_admin = res_admin.json()
        self.assertEqual(data_admin["user"]["role"], "admin")

    def test_04_invalid_login_rejection(self):
        """Test that invalid credentials return HTTP 401."""
        res = self.client.post("/api/auth/login", json={
            "email": "demo@nexadata.ai",
            "password": "IncorrectPassword!"
        })
        self.assertEqual(res.status_code, 401)
        self.assertIn("Invalid email or password", res.json()["detail"])

        res_unknown = self.client.post("/api/auth/login", json={
            "email": "nonexistent@nexadata.ai",
            "password": "AnyPassword123!"
        })
        self.assertEqual(res_unknown.status_code, 401)

    def test_05_register_new_user_and_duplicate_check(self):
        """Test user registration flow and rejection of duplicate emails."""
        rand_id = uuid.uuid4().hex[:6]
        email = f"user_{rand_id}@nexadata.ai"
        res = self.client.post("/api/auth/register", json={
            "email": email,
            "password": "MyStrongPassword2026!",
            "full_name": "Test User"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["user"]["email"], email)
        self.assertEqual(data["user"]["full_name"], "Test User")

        # Duplicate registration attempt
        res_dup = self.client.post("/api/auth/register", json={
            "email": email,
            "password": "AnotherPassword!",
            "full_name": "Duplicate User"
        })
        self.assertEqual(res_dup.status_code, 400)
        self.assertIn("already exists", res_dup.json()["detail"])

    def test_06_profile_me_endpoint(self):
        """Test /api/auth/me requiring valid token."""
        # Unauthenticated request
        res_unauth = self.client.get("/api/auth/me")
        self.assertEqual(res_unauth.status_code, 401)

        # Authenticated request with token
        login_res = self.client.post("/api/auth/login", json={
            "email": "demo@nexadata.ai",
            "password": "NexaDemo2026!"
        })
        token = login_res.json()["access_token"]
        res_profile = self.client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res_profile.status_code, 200)
        profile = res_profile.json()
        self.assertEqual(profile["email"], "demo@nexadata.ai")
        self.assertEqual(profile["full_name"], "Demo Analyst")

    def test_07_hybrid_guest_mode_access(self):
        """Verify Option B: Guests can still query chat endpoints without auth."""
        res_guest = self.client.post("/api/chat", json={
            "message": "What is NexaData?",
            "mode": "company"
        })
        self.assertEqual(res_guest.status_code, 200)
        self.assertIn("reply", res_guest.json())

    def test_08_multi_tenant_chat_isolation(self):
        """Verify chat sessions are strictly isolated between authenticated users."""
        # Create two distinct test users
        uid_a = f"alice_{uuid.uuid4().hex[:6]}"
        uid_b = f"bob_{uuid.uuid4().hex[:6]}"

        res_a = self.client.post("/api/auth/register", json={
            "email": f"{uid_a}@nexadata.ai",
            "password": "Password123!",
            "full_name": "Alice"
        })
        token_a = res_a.json()["access_token"]

        res_b = self.client.post("/api/auth/register", json={
            "email": f"{uid_b}@nexadata.ai",
            "password": "Password123!",
            "full_name": "Bob"
        })
        token_b = res_b.json()["access_token"]

        # Alice saves a conversation
        session_id_a = f"sess_alice_{uuid.uuid4().hex[:6]}"
        self.client.post("/api/conversations", json={
            "session_id": session_id_a,
            "title": "Alice Secret Chat",
            "mode": "company",
            "messages": [{"role": "user", "content": "Alice query"}]
        }, headers={"Authorization": f"Bearer {token_a}"})

        # Bob saves a conversation
        session_id_b = f"sess_bob_{uuid.uuid4().hex[:6]}"
        self.client.post("/api/conversations", json={
            "session_id": session_id_b,
            "title": "Bob Analytics Chat",
            "mode": "company",
            "messages": [{"role": "user", "content": "Bob query"}]
        }, headers={"Authorization": f"Bearer {token_b}"})

        # Alice lists conversations - should ONLY see Alice's conversation
        convs_a = self.client.get("/api/conversations", headers={"Authorization": f"Bearer {token_a}"}).json()["conversations"]
        alice_session_ids = [c["session_id"] for c in convs_a]
        self.assertIn(session_id_a, alice_session_ids)
        self.assertNotIn(session_id_b, alice_session_ids)

        # Bob lists conversations - should ONLY see Bob's conversation
        convs_b = self.client.get("/api/conversations", headers={"Authorization": f"Bearer {token_b}"}).json()["conversations"]
        bob_session_ids = [c["session_id"] for c in convs_b]
        self.assertIn(session_id_b, bob_session_ids)
        self.assertNotIn(session_id_a, bob_session_ids)

        # Bob attempts to delete Alice's conversation - should fail (not_found/unauthorized)
        del_attempt = self.client.delete(f"/api/conversations/{session_id_a}", headers={"Authorization": f"Bearer {token_b}"})
        self.assertEqual(del_attempt.json()["status"], "not_found")

        # Alice's conversation remains intact
        convs_a_after = self.client.get("/api/conversations", headers={"Authorization": f"Bearer {token_a}"}).json()["conversations"]
        self.assertIn(session_id_a, [c["session_id"] for c in convs_a_after])

if __name__ == "__main__":
    unittest.main()
