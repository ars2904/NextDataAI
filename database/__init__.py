"""NexaData Database Module (PostgreSQL Engine & Data Access Layer)."""
from database.postgres import (
    db_engine,
    get_products_list,
    get_master_records_list,
    get_transactions_list,
    get_analytics_summary,
    search_records,
    query_database_smart
)

__all__ = [
    "db_engine",
    "get_products_list",
    "get_master_records_list",
    "get_transactions_list",
    "get_analytics_summary",
    "search_records",
    "query_database_smart",
]
