"""Security guardrails and query validation module."""
import re
from typing import Tuple

BLOCKED_SQL_KEYWORDS = {
    "DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "CREATE", "TRUNCATE",
    "REPLACE", "EXEC", "EXECUTE", "ATTACH", "DETACH", "PRAGMA", "COPY",
    "INSTALL", "LOAD", "EXPORT", "IMPORT"
}

BLOCKED_PYTHON_PATTERNS = [
    r"__\w+__",          # Dunder methods
    r"os\.",             # os module calls
    r"sys\.",            # sys module calls
    r"subprocess\.",     # subprocess calls
    r"open\s*\(",        # file open
    r"eval\s*\(",        # nested eval
    r"exec\s*\(",        # nested exec
    r"to_csv",           # file write attempts
    r"to_excel",
    r"to_sql",
]


def validate_sql_query(query: str) -> Tuple[bool, str]:
    """
    Validate that a generated SQL query is strictly read-only (SELECT)
    and contains no malicious DDL, DML, or administrative commands.
    """
    cleaned = query.strip()
    
    # Strip markdown if present
    if cleaned.startswith("```sql"):
        cleaned = cleaned[len("```sql"):].strip()
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:].strip()
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3].strip()

    # Query must start with SELECT or WITH (for CTEs) or DESCRIBE or EXPLAIN
    first_word = cleaned.split()[0].upper() if cleaned.split() else ""
    if first_word not in {"SELECT", "WITH", "DESCRIBE"}:
        return False, f"Disallowed query type: Query must start with SELECT (got {first_word})."

    # Token-level check for blocked keywords
    tokens = set(re.findall(r"\b[A-Z_]+\b", cleaned.upper()))
    intersection = tokens.intersection(BLOCKED_SQL_KEYWORDS)
    if intersection:
        return False, f"Potentially destructive SQL command detected: {', '.join(intersection)}."

    # Check for semicolon injection (multiple queries)
    # Remove strings inside quotes before checking semicolons
    no_quotes = re.sub(r"'[^']*'", "", cleaned)
    if ";" in no_quotes.strip()[:-1]:  # semicolon before the end
        return False, "Multiple queries separated by semicolons are not permitted."

    return True, cleaned


def clean_query_text(text: str) -> str:
    """Strip code blocks and formatting from LLM output."""
    cleaned = text.strip()
    # Strip markdown blocks
    match = re.search(r"```(?:sql|python)?\s*(.*?)\s*```", cleaned, re.DOTALL | re.IGNORECASE)
    if match:
        cleaned = match.group(1).strip()
    
    # Remove trailing semicolon if present
    if cleaned.endswith(";"):
        cleaned = cleaned[:-1].strip()
        
    return cleaned
