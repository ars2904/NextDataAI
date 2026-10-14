"""Integration tests for NexaData AI expanded relational database."""
import sys
import unittest
from pathlib import Path
from fastapi.testclient import TestClient

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.main import app
from database.postgres import (
    get_analytics_summary,
    get_products_list,
    get_customers_list,
    get_orders_list,
    get_transactions_list,
    get_inventory_list,
    get_departments_list,
    get_employees_list,
    get_policies_list,
    get_faqs_list,
    query_database_smart
)

client = TestClient(app)

class TestExpandedDatabase(unittest.TestCase):
    def test_database_table_record_counts(self):
        """Verify minimum record thresholds required by enterprise specification."""
        summary = get_analytics_summary()
        self.assertGreaterEqual(summary["total_products"], 20, f"Expected >= 20 products, got {summary['total_products']}")
        self.assertGreaterEqual(summary["total_customers"], 50, f"Expected >= 50 customers, got {summary['total_customers']}")
        self.assertGreaterEqual(summary["total_orders"], 100, f"Expected >= 100 orders, got {summary['total_orders']}")
        self.assertGreaterEqual(summary["total_transactions"], 200, f"Expected >= 200 transactions, got {summary['total_transactions']}")
        self.assertGreaterEqual(summary["total_inventory_items"], 20)
        self.assertGreaterEqual(summary["total_departments"], 5)
        self.assertGreaterEqual(summary["total_employees"], 20)
        self.assertGreaterEqual(summary["total_policies"], 5)
        self.assertGreaterEqual(summary["total_faqs"], 10)
        self.assertGreater(summary["total_revenue_usd"], 1000000.0)

    def test_rest_api_endpoints(self):
        """Verify REST API endpoints for expanded tables."""
        # 1. DB Status
        res = client.get("/api/db/status")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(data["total_customers"], 50)
        self.assertGreaterEqual(data["total_orders"], 100)
        self.assertGreaterEqual(data["total_transactions"], 200)

        # 2. Customers
        res = client.get("/api/db/customers")
        self.assertEqual(res.status_code, 200)
        cust_data = res.json()
        self.assertGreaterEqual(len(cust_data["customers"]), 50)

        # 3. Orders
        res = client.get("/api/db/orders")
        self.assertEqual(res.status_code, 200)
        ord_data = res.json()
        self.assertGreater(len(ord_data["orders"]), 0)

        # 4. Inventory
        res = client.get("/api/db/inventory")
        self.assertEqual(res.status_code, 200)
        inv_data = res.json()
        self.assertGreaterEqual(len(inv_data["inventory"]), 20)

        # 5. Policies
        res = client.get("/api/db/policies")
        self.assertEqual(res.status_code, 200)
        pol_data = res.json()
        self.assertGreaterEqual(len(pol_data["policies"]), 10)

    def test_smart_database_queries(self):
        """Verify that smart database queries return formatted markdown tables."""
        # Inventory
        inv_reply = query_database_smart("What is your current inventory status and stock level?")
        self.assertIsNotNone(inv_reply)
        self.assertIn("Inventory", inv_reply)
        self.assertIn("SKU-", inv_reply)

        # Orders
        ord_reply = query_database_smart("Show me the latest orders list")
        self.assertIsNotNone(ord_reply)
        self.assertIn("ORD-", ord_reply)

        # Customers
        cust_reply = query_database_smart("Show customer accounts")
        self.assertIsNotNone(cust_reply)
        self.assertIn("CUST-", cust_reply)

        # Database Policies
        pol_reply = query_database_smart("List policies from the database")
        self.assertIsNotNone(pol_reply)
        self.assertIn("POL-01", pol_reply)
        self.assertIn("Zero Data Leakage", pol_reply)

    def test_company_chat_database_flow(self):
        """Verify Company Questions mode correctly routes DB queries."""
        res = client.post("/api/chat", json={
            "message": "What is your current inventory and warehouse stock level?",
            "mode": "company"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["mode"], "company")
        self.assertIn("SKU-", data["reply"])
        self.assertTrue(any("PostgreSQL Enterprise Database" in s["document"] for s in data["sources"]))

if __name__ == "__main__":
    unittest.main()
