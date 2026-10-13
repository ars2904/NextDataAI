"""Database Initialization & Verification CLI script.

Usage:
    python -m database.init_db
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.postgres import (
    db_engine,
    get_products_list,
    get_master_records_list,
    get_transactions_list,
    get_analytics_summary
)

def main():
    print("=" * 60)
    print("[NexaData AI] Database Initialization & Health Check")
    print("=" * 60)

    summary = get_analytics_summary()
    print(f"Database Engine: {summary['database_engine'].upper()}")
    print(f"Connection Target: {db_engine.connection_string}")
    print("-" * 60)

    products = get_products_list()
    print(f"Products ({len(products)} records):")
    for p in products:
        print(f"   [{p['product_code']}] {p['name']} - ${p['price']:,.2f} ({p['tier']})")

    print("-" * 60)
    clients = get_master_records_list()
    print(f"Client Master Accounts ({len(clients)} records):")
    for c in clients:
        print(f"   [{c['client_code']}] {c['company_name']} ({c['industry']}) - {c['tier']}")

    print("-" * 60)
    txns = get_transactions_list()
    print(f"Business Transactions ({len(txns)} records):")
    for t in txns[:5]:
        print(f"   [{t['transaction_ref']}] {t['client_code']} | {t['product_code']} | ${t['amount']:,.2f} | {t['status']}")
    print(f"   ... and {len(txns) - 5} more transactions")

    print("=" * 60)
    print(f"Total Completed Revenue: ${summary['total_revenue_usd']:,.2f} USD")
    print(f"Total Pending Revenue: ${summary['pending_revenue_usd']:,.2f} USD")
    print("[SUCCESS] Database is ready and verified!")
    print("=" * 60)

if __name__ == "__main__":
    main()
