"""Test suite for file and image upload, processing, validation, and temporary isolation."""
import io
import unittest
from PIL import Image
import pandas as pd
from backend.file_handler import (
    validate_file,
    process_uploaded_file,
    sanitize_filename,
    format_file_size,
    MAX_FILE_SIZE_BYTES
)
from backend.orchestrator import orchestrator
from rag.engine import knowledge_base
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


class TestFileUpload(unittest.TestCase):

    def test_sanitize_filename(self):
        self.assertEqual(sanitize_filename("../../etc/passwd.txt"), "passwd.txt")
        self.assertEqual(sanitize_filename("valid_report_2026.pdf"), "valid_report_2026.pdf")
        self.assertEqual(sanitize_filename(""), "uploaded_file")

    def test_format_file_size(self):
        self.assertEqual(format_file_size(500), "500 B")
        self.assertEqual(format_file_size(2048), "2.0 KB")
        self.assertEqual(format_file_size(2 * 1024 * 1024), "2.0 MB")

    def test_file_validation_valid_formats(self):
        for ext in ["pdf", "docx", "txt", "csv", "png", "jpg", "jpeg", "webp"]:
            valid, err, detected_ext = validate_file(f"sample.{ext}", b"testcontent")
            self.assertTrue(valid, f"Extension {ext} should be valid")
            self.assertEqual(detected_ext, ext)

    def test_file_validation_invalid_format(self):
        valid, err, _ = validate_file("malicious.exe", b"testcontent")
        self.assertFalse(valid)
        self.assertIn("Unsupported file format", err)

    def test_file_validation_size_limit(self):
        huge_bytes = b"x" * (MAX_FILE_SIZE_BYTES + 1024)
        valid, err, _ = validate_file("oversized.pdf", huge_bytes)
        self.assertFalse(valid)
        self.assertIn("exceeds the 10 MB limit", err)

    def test_process_txt_file(self):
        sample_txt = b"NexaData AI enterprise document text processing sample."
        res = process_uploaded_file("notes.txt", sample_txt)
        self.assertEqual(res["extension"], "txt")
        self.assertIn("enterprise document", res["text_content"])
        self.assertTrue(res["is_document"])
        self.assertFalse(res["is_image"])

    def test_process_csv_file(self):
        df = pd.DataFrame({
            "product_id": [1, 2, 3],
            "product_name": ["Alpha", "Beta", "Gamma"],
            "revenue": [12000.5, 45000.0, 98000.75]
        })
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        res = process_uploaded_file("sales_data.csv", csv_bytes)
        self.assertEqual(res["extension"], "csv")
        self.assertIn("revenue", res["text_content"])
        self.assertEqual(res["metadata"]["rows"], 3)
        self.assertEqual(res["metadata"]["columns"], 3)

    def test_process_image_file(self):
        # Create a small valid test PNG in memory
        img = Image.new("RGB", (100, 60), color="blue")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        png_bytes = buf.getvalue()

        res = process_uploaded_file("diagram.png", png_bytes)
        self.assertEqual(res["extension"], "png")
        self.assertTrue(res["is_image"])
        self.assertIsNotNone(res["b64_image"])
        self.assertEqual(res["metadata"]["width"], 100)
        self.assertEqual(res["metadata"]["height"], 60)

    def test_temporary_isolation_does_not_mutate_knowledge_base(self):
        initial_indexed = list(knowledge_base.indexed_files)
        initial_chunks = len(knowledge_base.chunks)

        txt_bytes = b"Secret client payload that should NEVER enter company permanent KB."
        res = process_uploaded_file("private_client.txt", txt_bytes)

        # Process through orchestrator in Company mode
        chat_resp = orchestrator.process_message(
            message="Check this private text",
            mode="company",
            attachment=res
        )

        self.assertIsNotNone(chat_resp.reply)
        # Knowledge base must not have added the private file
        self.assertEqual(list(knowledge_base.indexed_files), initial_indexed)
        self.assertEqual(len(knowledge_base.chunks), initial_chunks)

    def test_api_chat_upload_endpoint(self):
        csv_content = b"metric,score\nlatency,12\naccuracy,99\n"
        response = client.post(
            "/api/chat-upload",
            data={"message": "Summarize my dataset", "mode": "general"},
            files={"file": ("metrics.csv", csv_content, "text/csv")}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("reply", data)
        self.assertEqual(data["mode"], "general")
        self.assertEqual(data["attachment_info"]["filename"], "metrics.csv")

    def test_api_upload_preview_endpoint(self):
        img = Image.new("RGB", (80, 80), color="red")
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        jpg_bytes = buf.getvalue()

        response = client.post(
            "/api/upload-preview",
            files={"file": ("chart.jpg", jpg_bytes, "image/jpeg")}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "valid")
        self.assertTrue(data["is_image"])
        self.assertEqual(data["metadata"]["width"], 80)


if __name__ == "__main__":
    unittest.main()
