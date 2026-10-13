"""Unit test suite for voice recording, speech-to-text API, and language support."""
import unittest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


class TestVoiceSpeechRecognition(unittest.TestCase):

    def test_transcribe_endpoint_valid_audio_english(self):
        # Fake audio webm header / mock audio payload
        fake_audio = b"\x1a\x45\xdf\xa3" + b"MockAudioBytesContentForTranscriptionTesting"
        response = client.post(
            "/api/transcribe",
            data={"language": "en"},
            files={"file": ("recording.webm", fake_audio, "audio/webm")}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
        self.assertEqual(data["language"], "en")

    def test_transcribe_endpoint_valid_audio_hindi(self):
        fake_audio = b"\x1a\x45\xdf\xa3" + b"MockAudioBytesHindi"
        response = client.post(
            "/api/transcribe",
            data={"language": "hi-IN"},
            files={"file": ("voice_hi.webm", fake_audio, "audio/webm")}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
        self.assertTrue(data["language"].startswith("hi"))

    def test_transcribe_endpoint_empty_file_rejected(self):
        response = client.post(
            "/api/transcribe",
            data={"language": "en"},
            files={"file": ("empty.webm", b"", "audio/webm")}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Empty audio recording", response.json().get("detail", ""))

    def test_chat_workflow_preservation_after_transcription(self):
        # Verify chat endpoint continues to process recognized queries seamlessly
        recognized_query = "What solutions does NexaData provide?"
        res = client.post("/api/chat", json={"message": recognized_query, "mode": "company"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("reply", data)
        self.assertEqual(data["mode"], "company")


if __name__ == "__main__":
    unittest.main()
