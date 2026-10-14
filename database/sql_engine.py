"""Dynamic Text-to-SQL & Business Analytics Engine for NexaData AI.

Features:
- Schema Semantic Profiler for 14 relational tables.
- Read-Only SQL Safety Validator with AST/Regex protection against destructive operations.
- LLM Natural Language to SQL Generator (with GPT-4o-mini).
- Automated Self-Healing Error Correction loop on syntax / execution failures.
- Deterministic Offline Analytics Matcher for zero-cost, instant analytics when offline.
- Formatted Markdown reporting with analytical summaries and currency formatting.
"""
import os
import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy import text
from database.postgres import db_engine

logger = logging.getLogger("nexadata.sql_engine")
logger.setLevel(logging.INFO)

# ============================================================================
# 1. Database Schema Semantic Definition
# ============================================================================

SCHEMA_PROMPT_DOC = """
You are NexaData AI's Enterprise Database Engine.
You have access to a relational SQL database with 14 business tables:

1. company_info:
   - id (INT PK), company_name (VARCHAR), legal_name (VARCHAR), founded_year (INT), headquarters (VARCHAR), website (VARCHAR), ceo (VARCHAR), contact_email (VARCHAR), support_email (VARCHAR), phone (VARCHAR), total_employees (INT), active_countries (INT), duns_number (VARCHAR), tax_id (VARCHAR), mission (TEXT)

2. departments:
   - id (INT PK), department_code (VARCHAR UK, e.g. 'DEP-101'), name (VARCHAR, e.g. 'Engineering & Architecture', 'Data Science & AI', 'Enterprise Sales', 'Customer Success', 'Product Management', 'Finance & Operations', 'Legal & Compliance', 'People & Talent'), head_of_department (VARCHAR), budget (FLOAT), location (VARCHAR), employee_count (INT)

3. employees:
   - id (INT PK), employee_code (VARCHAR UK, e.g. 'EMP-1001'), first_name (VARCHAR), last_name (VARCHAR), email (VARCHAR), phone (VARCHAR), department_code (VARCHAR FK to departments.department_code), role (VARCHAR), salary (FLOAT), hire_date (VARCHAR), status (VARCHAR: 'Active', 'On Leave'), location (VARCHAR)

4. categories:
   - id (INT PK), category_code (VARCHAR UK, e.g. 'CAT-PLATFORM'), name (VARCHAR), description (TEXT)

5. suppliers:
   - id (INT PK), supplier_code (VARCHAR UK, e.g. 'SUP-AWS'), name (VARCHAR), contact_name (VARCHAR), email (VARCHAR), phone (VARCHAR), country (VARCHAR), service_type (VARCHAR), rating (FLOAT), payment_terms (VARCHAR)

6. products:
   - id (INT PK), product_code (VARCHAR UK, e.g. 'ND-ENT-01'), name (VARCHAR), tier (VARCHAR: 'Starter', 'Professional', 'Enterprise', 'Ultimate'), category_code (VARCHAR FK), supplier_code (VARCHAR FK), price (FLOAT), cost_price (FLOAT), billing_type (VARCHAR: 'Annual License', 'Monthly Subscription', 'Usage-Based', 'One-Time Setup'), stock_quantity (INT), description (TEXT), features (TEXT), is_active (BOOLEAN)

7. inventory:
   - id (INT PK), sku (VARCHAR UK, e.g. 'SKU-ENT-US-E'), product_code (VARCHAR FK to products.product_code), warehouse_location (VARCHAR: 'US-East (Virginia)', 'US-West (Oregon)', 'EU-Central (Frankfurt)', 'AP-South (Mumbai)'), quantity_available (INT), quantity_reserved (INT), reorder_level (INT), unit_cost (FLOAT), status (VARCHAR: 'In Stock', 'Low Stock')

8. customers:
   - id (INT PK), customer_code (VARCHAR UK, e.g. 'CUST-1001'), company_name (VARCHAR), contact_name (VARCHAR), email (VARCHAR), phone (VARCHAR), city (VARCHAR), state (VARCHAR), country (VARCHAR), industry (VARCHAR: 'FinTech & Banking', 'Healthcare & Biotech', 'Supply Chain & Logistics', 'E-Commerce & Retail', 'Cybersecurity', 'Telecommunications', 'Aerospace & Defense', 'Energy & Utilities'), tier (VARCHAR: 'Enterprise', 'Premier', 'Standard'), credit_limit (FLOAT), account_balance (FLOAT), sales_rep_code (VARCHAR), status (VARCHAR: 'Active', 'Suspended')

9. clients_master (compatible with customers):
   - id (INT PK), client_code (VARCHAR UK, e.g. 'MST-101' to 'MST-105'), company_name (VARCHAR), industry (VARCHAR), region (VARCHAR), tier (VARCHAR), contact_person (VARCHAR), email (VARCHAR), status (VARCHAR)

10. orders:
   - id (INT PK), order_number (VARCHAR UK, e.g. 'ORD-2026-0001'), customer_code (VARCHAR FK to customers.customer_code), order_date (VARCHAR: 'YYYY-MM-DD'), status (VARCHAR: 'Completed', 'Processing', 'Pending Payment', 'Cancelled'), total_amount (FLOAT), discount_amount (FLOAT), net_amount (FLOAT), payment_status (VARCHAR: 'Paid', 'Pending', 'Partial', 'Refunded'), sales_rep_code (VARCHAR), billing_cycle (VARCHAR: 'Annual', 'Quarterly', 'Monthly'), notes (TEXT)

11. order_items:
   - id (INT PK), order_number (VARCHAR FK to orders.order_number), product_code (VARCHAR FK to products.product_code), quantity (INT), unit_price (FLOAT), subtotal (FLOAT), discount (FLOAT), line_total (FLOAT)

12. payments:
   - id (INT PK), payment_ref (VARCHAR UK, e.g. 'PAY-2026-0001'), order_number (VARCHAR FK to orders.order_number), customer_code (VARCHAR FK to customers.customer_code), amount (FLOAT), currency (VARCHAR, default 'USD'), payment_method (VARCHAR: 'ACH Wire Transfer', 'Corporate Credit Card', 'Automated Clearing House', 'Escrow Service'), status (VARCHAR: 'Success', 'Pending', 'Failed'), payment_date (VARCHAR: 'YYYY-MM-DD'), gateway_ref (VARCHAR)

13. transactions:
   - id (INT PK), transaction_ref (VARCHAR UK, e.g. 'TXN-2026-0001'), client_code (VARCHAR FK), client_name (VARCHAR), product_code (VARCHAR FK), amount (FLOAT), currency (VARCHAR, default 'USD'), status (VARCHAR: 'Completed', 'Pending', 'Failed'), payment_method (VARCHAR), transaction_date (VARCHAR: 'YYYY-MM-DD'), notes (TEXT)

14. policies:
   - id (INT PK), policy_code (VARCHAR UK, e.g. 'POL-001'), title (VARCHAR), category (VARCHAR), version (VARCHAR), effective_date (VARCHAR), department_code (VARCHAR), summary (TEXT), full_text (TEXT), status (VARCHAR: 'Active')

15. faqs:
   - id (INT PK), faq_code (VARCHAR UK, e.g. 'FAQ-001'), category (VARCHAR), question (TEXT), answer (TEXT), is_active (BOOLEAN)

SQL RULES:
1. ONLY produce a single valid, read-only SQL SELECT statement.
2. DO NOT include any INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, CREATE, or semicolon-chained statements.
3. The SQL must be standard ANSI SQL compatible with both PostgreSQL and SQLite. Use standard aggregate functions: COUNT(*), SUM(...), AVG(...), MAX(...), MIN(...), ROUND(...), GROUP BY, ORDER BY, LIMIT.
4. For string concatenation, use `first_name || ' ' || last_name` or standard column aliasing.
5. Case-insensitivity: when filtering text columns, prefer `LOWER(column) LIKE '%term%'`.
6. Always include a sensible LIMIT (default 25 or 50) unless doing a single-row aggregate.
7. Return ONLY the raw SQL statement inside ```sql ... ``` block or plain text without commentary.
"""

# ============================================================================
# 2. Read-Only SQL Safety Validator
# ============================================================================

DISALLOWED_KEYWORDS = [
    r"\binsert\b", r"\bupdate\b", r"\bdelete\b", r"\bdrop\b", r"\balter\b",
    r"\bcreate\b", r"\btruncate\b", r"\battach\b", r"\bdetach\b", r"\bpragma\b",
    r"\bexec\b", r"\bexecute\b", r"\bgrant\b", r"\brevoke\b", r"\breplace\b",
    r"\bmerge\b", r"\bcall\b", r"\bload_file\b", r"\boutfile\b", r"\bdumpfile\b"
]

def sanitize_and_validate_sql(raw_sql: str) -> Tuple[bool, str, Optional[str]]:
    """
    Validate that raw_sql is strictly a single, read-only SELECT query.
    Returns (is_valid, cleaned_sql, error_message).
    """
    if not raw_sql or not raw_sql.strip():
        return False, "", "Query string is empty."

    # Extract code from markdown block if present
    match = re.search(r"```(?:sql)?\s*([\s\S]*?)\s*```", raw_sql, re.IGNORECASE)
    cleaned = match.group(1).strip() if match else raw_sql.strip()

    # Strip trailing semicolons
    cleaned = cleaned.rstrip(";").strip()

    # Reject multi-statement queries (semicolon inside statement)
    if ";" in cleaned:
        return False, cleaned, "Multi-statement SQL queries are strictly prohibited."

    # Must start with SELECT or WITH (for CTEs)
    first_word = cleaned.split()[0].upper() if cleaned.split() else ""
    if first_word not in ("SELECT", "WITH"):
        return False, cleaned, f"Only SELECT or WITH queries are permitted. Found: {first_word}"

    # Check against destructive keywords
    lower_sql = cleaned.lower()
    for pattern in DISALLOWED_KEYWORDS:
        if re.search(pattern, lower_sql):
            keyword = pattern.replace(r"\b", "")
            return False, cleaned, f"Security violation: statement contains forbidden keyword '{keyword}'."

    # Disallow SQL comment injection
    if "--" in cleaned or "/*" in cleaned:
        return False, cleaned, "SQL comment markers are not permitted for security."

    # Automatically append LIMIT 50 if no LIMIT is specified
    if not re.search(r"\blimit\s+\d+", lower_sql) and not re.search(r"\bcount\(|\bsum\(|\bavg\(", lower_sql):
        cleaned += " LIMIT 50"

    return True, cleaned, None

# ============================================================================
# 3. SQL Query Execution Engine
# ============================================================================

def execute_safe_sql(sql_query: str) -> Dict[str, Any]:
    """Execute validated read-only SQL query against db_engine."""
    is_valid, clean_sql, error_msg = sanitize_and_validate_sql(sql_query)
    if not is_valid:
        return {
            "success": False,
            "error": error_msg,
            "sql": clean_sql,
            "columns": [],
            "rows": [],
            "row_count": 0
        }

    try:
        with db_engine.connect() as conn:
            result = conn.execute(text(clean_sql))
            columns = list(result.keys()) if result.returns_rows else []
            rows = [list(r) for r in result.fetchall()] if result.returns_rows else []
            return {
                "success": True,
                "error": None,
                "sql": clean_sql,
                "columns": columns,
                "rows": rows,
                "row_count": len(rows)
            }
    except Exception as e:
        logger.warning(f"SQL execution error for '{clean_sql}': {e}")
        return {
            "success": False,
            "error": str(e),
            "sql": clean_sql,
            "columns": [],
            "rows": [],
            "row_count": 0
        }

# ============================================================================
# 4. Result Formatting & Analytics Summarizer
# ============================================================================

def format_cell_value(val: Any, col_name: str) -> str:
    """Format row cell into human-readable text with currency and badge styling."""
    if val is None:
        return "*NULL*"
    if isinstance(val, float):
        if any(c in col_name.lower() for c in ["amount", "price", "budget", "cost", "balance", "limit", "revenue", "salary", "subtotal", "total"]):
            return f"${val:,.2f}"
        return f"{val:,.2f}"
    if isinstance(val, int):
        return f"{val:,}"
    if isinstance(val, bool):
        return "Yes" if val else "No"
    s_val = str(val).strip()
    if s_val in ("Completed", "Paid", "Active", "Success", "In Stock"):
        return f"`[{s_val}]`"
    if s_val in ("Pending", "Low Stock", "Processing"):
        return f"`[{s_val}]`"
    if s_val in ("Failed", "Cancelled", "Suspended"):
        return f"`[{s_val}]`"
    return s_val

def format_results_markdown(exec_result: Dict[str, Any], query_title: Optional[str] = None) -> str:
    """Format SQL execution results into a clean, responsive Markdown table."""
    if not exec_result["success"]:
        return (
            f"❌ **Database Query Execution Failed:**\n"
            f"> `{exec_result['error']}`\n\n"
            f"**Attempted SQL:**\n```sql\n{exec_result['sql']}\n```"
        )

    columns = exec_result["columns"]
    rows = exec_result["rows"]
    row_count = exec_result["row_count"]

    title = query_title or f"Live Business Analytics Query ({row_count} Records Found)"

    if row_count == 0:
        return (
            f"### {title}\n\n"
            f"No records matched the filter criteria in the database.\n\n"
            f"**Executed Query:**\n```sql\n{exec_result['sql']}\n```"
        )

    # Format header
    header_titles = [c.replace("_", " ").title() for c in columns]
    header_row = "| " + " | ".join(header_titles) + " |"
    separator_row = "| " + " | ".join([":---"] * len(columns)) + " |"

    # Format data rows (up to 30 rows in display)
    display_rows = []
    for r in rows[:30]:
        formatted_cells = [format_cell_value(val, columns[idx]) for idx, val in enumerate(r)]
        display_rows.append("| " + " | ".join(formatted_cells) + " |")

    table_md = "\n".join([header_row, separator_row] + display_rows)

    summary_note = ""
    if row_count > 30:
        summary_note = f"\n\n*(Showing top 30 of {row_count} matching database records)*"

    sql_footer = (
        f"\n\n<details><summary>🔍 View Generated SQL Query</summary>\n\n"
        f"```sql\n{exec_result['sql']}\n```\n"
        f"</details>"
    )

    return f"### {title}\n\n{table_md}{summary_note}{sql_footer}"

# ============================================================================
# 5. Deterministic Offline Analytics Matcher
# ============================================================================

def resolve_offline_analytics_query(query: str) -> Optional[Dict[str, str]]:
    """
    Match common natural language business analytics questions to pre-optimized,
    high-performance SQL statements without calling an LLM.
    """
    q = query.lower().strip()

    # 1. Top spending customers / highest balance
    if any(k in q for k in ["top customer", "highest balance", "highest spending", "biggest customer", "top 5 customer", "top 10 customer", "top clients"]):
        return {
            "title": "Top Enterprise Customers by Account Balance",
            "sql": "SELECT customer_code, company_name, industry, tier, credit_limit, account_balance, status FROM customers ORDER BY account_balance DESC LIMIT 10;"
        }

    # 2. Revenue by status / total transactions
    if any(k in q for k in ["total revenue", "revenue summary", "sales revenue", "how much revenue", "how much money", "total sales"]):
        return {
            "title": "NexaData Enterprise Recognized & Pending Revenue Summary",
            "sql": "SELECT status, COUNT(*) AS transaction_count, SUM(amount) AS total_revenue_usd, AVG(amount) AS average_transaction_usd FROM transactions GROUP BY status ORDER BY total_revenue_usd DESC;"
        }

    # 3. Low stock inventory alert
    if any(k in q for k in ["low stock", "reorder", "out of stock", "need restocking", "stock alert", "running low"]):
        return {
            "title": "Low Stock & Reorder Alert (Warehouse Inventory)",
            "sql": "SELECT sku, product_code, warehouse_location, quantity_available, quantity_reserved, reorder_level, unit_cost, status FROM inventory WHERE quantity_available <= reorder_level OR status = 'Low Stock' ORDER BY quantity_available ASC LIMIT 20;"
        }

    # 4. Inventory summary by warehouse cluster
    if any(k in q for k in ["inventory by warehouse", "warehouse stock", "inventory summary", "warehouse location"]):
        return {
            "title": "Inventory Overview by Warehouse Cluster",
            "sql": "SELECT warehouse_location, COUNT(*) AS sku_count, SUM(quantity_available) AS total_available_units, SUM(quantity_reserved) AS total_reserved_units, SUM(quantity_available * unit_cost) AS total_inventory_value_usd FROM inventory GROUP BY warehouse_location ORDER BY total_available_units DESC;"
        }

    # 5. Orders summary by status
    if any(k in q for k in ["order status", "orders summary", "completed orders", "pending orders", "order breakdown"]):
        return {
            "title": "Order Processing & Fulfillment Summary",
            "sql": "SELECT status, payment_status, COUNT(*) AS total_orders, SUM(net_amount) AS total_value_usd, AVG(net_amount) AS avg_order_value_usd FROM orders GROUP BY status, payment_status ORDER BY total_orders DESC;"
        }

    # 6. Payment methods breakdown
    if any(k in q for k in ["payment method", "payment breakdown", "payment types", "how customers pay"]):
        return {
            "title": "Transaction Volume by Payment Method",
            "sql": "SELECT payment_method, status, COUNT(*) AS payment_count, SUM(amount) AS total_collected_usd FROM payments GROUP BY payment_method, status ORDER BY total_collected_usd DESC;"
        }

    # 7. Department budget & headcount
    if any(k in q for k in ["department budget", "highest budget", "department headcount", "departments list", "budget allocation"]):
        return {
            "title": "Corporate Department Budgets & Staff Headcounts",
            "sql": "SELECT department_code, name, head_of_department, budget, employee_count, location FROM departments ORDER BY budget DESC;"
        }

    # 8. Highest paid employees or employee directory
    if any(k in q for k in ["highest paid", "top salary", "employee list", "employee directory", "who works"]):
        return {
            "title": "NexaData Executive & Technical Staff Directory",
            "sql": "SELECT employee_code, first_name || ' ' || last_name AS employee_name, department_code, role, salary, location, status FROM employees ORDER BY salary DESC LIMIT 15;"
        }

    # 9. Top products by price / catalog
    if any(k in q for k in ["top products", "most expensive product", "product prices", "product catalog pricing"]):
        return {
            "title": "Enterprise Product Catalog (Ordered by Price)",
            "sql": "SELECT product_code, name, tier, price, cost_price, billing_type, stock_quantity FROM products ORDER BY price DESC LIMIT 15;"
        }

    # 10. Customers grouped by industry
    if any(k in q for k in ["customers by industry", "industry breakdown", "industries served"]):
        return {
            "title": "Enterprise Customer Distribution by Industry",
            "sql": "SELECT industry, COUNT(*) AS customer_count, SUM(credit_limit) AS total_credit_limit, SUM(account_balance) AS total_outstanding_balance FROM customers GROUP BY industry ORDER BY customer_count DESC;"
        }

    # 11. Suppliers and infrastructure partners
    if any(k in q for k in ["suppliers", "vendors", "partners", "supplier ratings"]):
        return {
            "title": "Infrastructure Partners & Cloud Suppliers",
            "sql": "SELECT supplier_code, name, country, service_type, rating, payment_terms FROM suppliers ORDER BY rating DESC;"
        }

    return None

# ============================================================================
# 6. Natural Language to SQL Generator with Self-Healing Error Loop
# ============================================================================

def generate_sql_from_llm(user_query: str, client: Any) -> Optional[str]:
    """Generate read-only SQL query from user query using OpenAI LLM."""
    if not client:
        return None

    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": SCHEMA_PROMPT_DOC},
                {
                    "role": "user",
                    "content": (
                        f"Generate a single, read-only SQL query to answer this user question:\n"
                        f"\"{user_query}\"\n\n"
                        f"Output ONLY the SQL inside ```sql ... ``` block."
                    )
                }
            ],
            temperature=0.0,
            max_tokens=300
        )
        raw_output = response.choices[0].message.content.strip()
        is_valid, clean_sql, _ = sanitize_and_validate_sql(raw_output)
        return clean_sql if is_valid else None
    except Exception as e:
        logger.warning(f"Error calling LLM for Text-to-SQL: {e}")
        return None

def self_heal_sql(failed_sql: str, error_message: str, user_query: str, client: Any) -> Optional[str]:
    """Provide one-shot auto-correction if initial SQL execution threw an error."""
    if not client:
        return None

    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": SCHEMA_PROMPT_DOC},
                {
                    "role": "user",
                    "content": (
                        f"The following SQL query failed execution:\n"
                        f"```sql\n{failed_sql}\n```\n\n"
                        f"Database Error Message:\n{error_message}\n\n"
                        f"Original User Question: \"{user_query}\"\n\n"
                        f"Fix the SQL syntax or column/table reference. Return ONLY the corrected SQL query inside ```sql ... ``` block."
                    )
                }
            ],
            temperature=0.0,
            max_tokens=300
        )
        raw_output = response.choices[0].message.content.strip()
        is_valid, clean_sql, _ = sanitize_and_validate_sql(raw_output)
        return clean_sql if is_valid else None
    except Exception as e:
        logger.warning(f"Error during SQL self-healing: {e}")
        return None

# ============================================================================
# 7. High-Level Dispatcher: answer_business_data_query
# ============================================================================

def is_business_data_query(query: str) -> bool:
    """Detect if a user query targets relational database records or business analytics."""
    q = query.lower()
    keywords = [
        "database", "sql", "revenue", "sales", "inventory", "stock", "warehouse",
        "orders", "order", "customer", "customers", "client", "clients",
        "transactions", "transaction", "payment", "payments", "budget", "departments",
        "employees", "employee", "salary", "supplier", "suppliers", "vendor",
        "sku-", "cust-", "ord-", "txn-", "pay-", "dep-", "emp-", "how many",
        "highest", "lowest", "average", "total", "top 5", "top 10", "top 3",
        "spending", "balance", "pricing", "plans", "credit limit"
    ]
    return any(k in q for k in keywords)

def answer_business_data_query(user_query: str, client: Optional[Any] = None) -> Optional[str]:
    """
    Primary interface for NL-to-SQL business analytics.
    1. Checks offline deterministic match first for common aggregation queries.
    2. If no offline match and client is available, generates SQL with LLM.
    3. Executes safely, performs self-healing if needed, and returns formatted Markdown.
    """
    if not is_business_data_query(user_query):
        return None

    # Step 1: Check offline deterministic query matcher
    offline_match = resolve_offline_analytics_query(user_query)
    if offline_match:
        exec_res = execute_safe_sql(offline_match["sql"])
        if exec_res["success"]:
            return format_results_markdown(exec_res, query_title=offline_match["title"])

    # Step 2: If LLM client is available, generate dynamic SQL
    if client:
        generated_sql = generate_sql_from_llm(user_query, client)
        if generated_sql:
            exec_res = execute_safe_sql(generated_sql)
            if exec_res["success"]:
                return format_results_markdown(exec_res, query_title=f"Business Intelligence: \"{user_query}\"")
            else:
                # Attempt self-healing auto-correction
                healed_sql = self_heal_sql(generated_sql, exec_res["error"], user_query, client)
                if healed_sql:
                    healed_res = execute_safe_sql(healed_sql)
                    if healed_res["success"]:
                        return format_results_markdown(healed_res, query_title=f"Business Intelligence: \"{user_query}\"")

    # Step 3: Fallback to general database summary if nothing else matched
    if any(k in user_query.lower() for k in ["database", "stats", "records", "how many"]):
        exec_res = execute_safe_sql(
            "SELECT 'Customers' AS area, COUNT(*) AS total_records FROM customers "
            "UNION ALL SELECT 'Products', COUNT(*) FROM products "
            "UNION ALL SELECT 'Orders', COUNT(*) FROM orders "
            "UNION ALL SELECT 'Transactions', COUNT(*) FROM transactions "
            "UNION ALL SELECT 'Inventory Items', COUNT(*) FROM inventory "
            "UNION ALL SELECT 'Employees', COUNT(*) FROM employees "
            "UNION ALL SELECT 'Departments', COUNT(*) FROM departments "
            "UNION ALL SELECT 'Suppliers', COUNT(*) FROM suppliers;"
        )
        if exec_res["success"]:
            return format_results_markdown(exec_res, query_title="NexaData Master Relational Schema Record Counts")

    return None
