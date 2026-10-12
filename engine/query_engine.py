"""High-performance query engine using DuckDB and AI-driven self-healing."""
import duckdb
import pandas as pd
from typing import Dict, Any, Optional, Tuple, List
from core.security import validate_sql_query, clean_query_text
from core.config import DEFAULT_MODEL


def execute_duckdb(query: str, df: pd.DataFrame) -> pd.DataFrame:
    """
    Execute a validated SQL query over a DataFrame using DuckDB.
    Returns the analytical result as a clean Pandas DataFrame.
    """
    is_valid, msg_or_query = validate_sql_query(query)
    if not is_valid:
        raise ValueError(f"Security validation error: {msg_or_query}")
        
    cleaned_query = msg_or_query
    
    # Create an isolated in-memory duckdb connection
    con = duckdb.connect(database=":memory:")
    try:
        # Register the dataframe as table 'df'
        con.register("df", df)
        result_df = con.execute(cleaned_query).df()
        return result_df
    finally:
        con.close()


def build_system_prompt(profile: Dict[str, Any]) -> str:
    """Construct a precise system prompt with column semantics and sample values."""
    col_details = []
    for col in profile["columns"]:
        dtype = profile["dtypes"].get(col, "unknown")
        samples = profile["sample_values"].get(col, [])
        sample_str = f" (e.g. {', '.join(samples)})" if samples else ""
        col_details.append(f"- `{col}` ({dtype}){sample_str}")

    columns_formatted = "\n".join(col_details)
    
    return f"""You are an expert DuckDB SQL data analyst for NexaData AI.
You translate natural language questions into accurate, high-performance DuckDB SQL queries.

TABLE SCHEMA:
Table name: `df`
Total rows: {profile['rows']:,}
Columns:
{columns_formatted}

RULES:
1. Generate strictly ONE valid DuckDB SQL query.
2. The table name is always `df`.
3. Use ONLY existing columns listed in the schema above.
4. For text filtering, be case-insensitive using LOWER() or ILIKE (e.g., LOWER(religion) = 'islam' or city ILIKE 'dhaka').
5. Use proper aggregates (SUM, AVG, COUNT, MIN, MAX, ROUND) with meaningful column aliases.
6. Order your results logically (e.g. ORDER BY total DESC) and use LIMIT if top/bottom N are requested.
7. Return ONLY the raw SQL query. Do NOT include markdown code blocks, explanations, or commentary.
"""


def generate_sql_from_llm(
    question: str,
    profile: Dict[str, Any],
    client: Any,
    model: str = DEFAULT_MODEL,
    error_context: Optional[str] = None,
    previous_attempt: Optional[str] = None
) -> str:
    """Call the LLM to generate or fix a DuckDB SQL query."""
    system_prompt = build_system_prompt(profile)
    
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    user_prompt = f"Question: {question}"
    
    # Self-healing feedback loop if previous execution failed
    if error_context and previous_attempt:
        user_prompt += f"""

CRITICAL: Your previous query failed with an error:
Failed Query:
{previous_attempt}

Error Message:
{error_context}

Please correct the query to fix the error above. Ensure column names match the schema exactly."""

    messages.append({"role": "user", "content": user_prompt})

    # Support OpenAI chat completions API
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.0,
        max_tokens=600
    )
    raw_query = response.choices[0].message.content.strip()
    return clean_query_text(raw_query)


def run_analytical_query(
    question: str,
    df: pd.DataFrame,
    profile: Dict[str, Any],
    client: Any,
    model: str = DEFAULT_MODEL,
    max_retries: int = 2
) -> Dict[str, Any]:
    """
    Executes an end-to-end analytical question:
    LLM SQL generation -> AST security check -> DuckDB execution -> Self-healing retry if error occurs.
    """
    attempt = 0
    error_context = None
    last_query = None
    
    while attempt <= max_retries:
        try:
            sql_query = generate_sql_from_llm(
                question=question,
                profile=profile,
                client=client,
                model=model,
                error_context=error_context,
                previous_attempt=last_query
            )
            last_query = sql_query
            
            # Execute query in DuckDB
            result_df = execute_duckdb(sql_query, df)
            
            return {
                "success": True,
                "query": sql_query,
                "result": result_df,
                "attempts": attempt + 1,
                "error": None
            }
        except Exception as e:
            attempt += 1
            error_context = str(e)
            if attempt > max_retries:
                return {
                    "success": False,
                    "query": last_query,
                    "result": None,
                    "attempts": attempt,
                    "error": error_context
                }
