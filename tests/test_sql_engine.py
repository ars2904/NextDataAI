"""Unit tests for Phase 2: Dynamic Text-to-SQL & Business Analytics Engine."""
import sys
import unittest
from pathlib import Path
from fastapi.testclient import TestClient

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.main import app
from database.sql_engine import (
    sanitize_and_validate_sql,
    execute_safe_sql,
    resolve_offline_analytics_query,
    format_results_markdown,
    answer_business_data_query,
    is_business_data_query
)

client = TestClient(app)

class TestSqlEngine(unittest.TestCase):
    """Test suite for Read-Only SQL Engine, Safety Guardrails, and Analytics."""

    def test_sql_safety_validator_valid_select(self):
        """Verify valid read-only SELECT queries pass validation."""
        valid_queries = [
            "SELECT customer_code, company_name FROM customers LIMIT 10;",
            "SELECT status, sum(amount) FROM transactions GROUP BY status",
            "WITH regional AS (SELECT * FROM customers WHERE country = 'USA') SELECT count(*) FROM regional",
            "```sql\nSELECT * FROM products WHERE price > 500\n```"
        ]
        for q in valid_queries:
            is_valid, clean_sql, err = sanitize_and_validate_sql(q)
            self.assertTrue(is_valid, f"Expected valid query for '{q}', got error: {err}")
            self.assertFalse(";" in clean_sql)

    def test_sql_safety_validator_rejects_destructive_dml_ddl(self):
        """Verify all destructive, modification, or injection statements are rejected."""
        malicious_queries = [
            "DROP TABLE customers;",
            "DELETE FROM orders WHERE id > 0",
            "UPDATE products SET price = 0",
            "INSERT INTO customers (customer_code) VALUES ('HACK')",
            "ALTER TABLE transactions ADD COLUMN malicious TEXT",
            "TRUNCATE TABLE inventory",
            "SELECT * FROM customers; DROP TABLE orders;",
            "SELECT * FROM customers -- comment injection",
            "SELECT * FROM customers /* comment block */",
            "EXEC xp_cmdshell('dir')"
        ]
        for q in malicious_queries:
            is_valid, _, err = sanitize_and_validate_sql(q)
            self.assertFalse(is_valid, f"Expected query '{q}' to be rejected for security!")
            self.assertIsNotNone(err)

    def test_execute_safe_sql_live_database(self):
        """Verify executing read-only SQL queries on the live database engine."""
        res = execute_safe_sql("SELECT count(*) AS total_customers FROM customers;")
        self.assertTrue(res["success"])
        self.assertGreaterEqual(res["rows"][0][0], 50)
        self.assertEqual(res["columns"], ["total_customers"])

    def test_offline_analytics_matcher(self):
        """Verify semantic matching for core business analytics questions."""
        match_rev = resolve_offline_analytics_query("What is our total revenue summary?")
        self.assertIsNotNone(match_rev)
        self.assertIn("transactions", match_rev["sql"].lower())

        match_cust = resolve_offline_analytics_query("Show me our top customers with highest spending")
        self.assertIsNotNone(match_cust)
        self.assertIn("customers", match_cust["sql"].lower())

        match_inv = resolve_offline_analytics_query("Which items are low stock and need reordering?")
        self.assertIsNotNone(match_inv)
        self.assertIn("inventory", match_inv["sql"].lower())

    def test_format_results_markdown(self):
        """Verify Markdown table generation with currency and header formatting."""
        exec_res = {
            "success": True,
            "error": None,
            "sql": "SELECT name, price, stock_quantity FROM products LIMIT 2",
            "columns": ["name", "price", "stock_quantity"],
            "rows": [["NexaData Enterprise", 45000.0, 100], ["Cloud Connector", 12000.0, 50]],
            "row_count": 2
        }
        md = format_results_markdown(exec_res, "Product Catalog Sample")
        self.assertIn("| Name | Price | Stock Quantity |", md)
        self.assertIn("$45,000.00", md)
        self.assertIn("NexaData Enterprise", md)
        self.assertIn("<details><summary>", md)

    def test_answer_business_data_query_end_to_end(self):
        """Verify answer_business_data_query generates and executes analytics queries."""
        reply = answer_business_data_query("What is our total sales revenue and transaction summary?")
        self.assertIsNotNone(reply)
        self.assertIn("Revenue Summary", reply)
        self.assertIn("Transaction Count", reply)

    def test_api_chat_company_mode_sql_analytics(self):
        """Verify /api/chat in Company mode uses Text-to-SQL for dynamic analytics."""
        res = client.post("/api/chat", json={
            "message": "What is our total recognized and pending revenue summary?",
            "mode": "company"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["mode"], "company")
        self.assertIn("Revenue Summary", data["reply"])
        self.assertTrue(any("PostgreSQL Enterprise Database" in s["document"] for s in data["sources"]))

if __name__ == "__main__":
    unittest.main()
