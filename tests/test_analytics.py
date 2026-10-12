"""Unit tests for Data Analytics, DuckDB engine, and security guardrails."""
import sys
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core.security import validate_sql_query
from engine.query_engine import execute_duckdb
from visualizer.charts import auto_detect_chart_type, create_chart

def test_security_rules():
    """Verify malicious SQL is blocked."""
    valid, _ = validate_sql_query("DROP TABLE df")
    assert not valid
    valid, _ = validate_sql_query("SELECT * FROM df; DROP TABLE df")
    assert not valid

def test_duckdb_execution():
    """Verify read-only SQL query execution in DuckDB."""
    test_df = pd.DataFrame({
        "category": ["A", "B", "A", "C"],
        "value": [10, 20, 30, 40]
    })
    res = execute_duckdb("SELECT category, sum(value) as total FROM df GROUP BY category", test_df)
    assert len(res) == 3
    assert "total" in res.columns

def test_auto_chart():
    """Verify intelligent chart selection."""
    test_df = pd.DataFrame({
        "city": ["Dhaka", "Chittagong", "Rajshahi"],
        "count": [100, 200, 150]
    })
    ctype, x, y = auto_detect_chart_type(test_df)
    assert ctype in ["pie", "bar"]
    fig = create_chart(test_df, ctype, x, y)
    assert fig is not None

if __name__ == "__main__":
    test_security_rules()
    test_duckdb_execution()
    test_auto_chart()
    print("All Analytics unit tests passed successfully.")
