"""PostgreSQL Database Engine & Data Access Layer for NexaData AI.

Supports standard PostgreSQL via DATABASE_URL or individual POSTGRES_* environment variables.
Provides automatic, zero-crash fallback to local SQLite for environments where a live
PostgreSQL daemon is not locally running.
Pre-seeds 5 Products, 5 Master Records (Clients), and 20 Transactions.
"""
import os
import sys
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text, select
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

logger = logging.getLogger("nexadata.database")
logger.setLevel(logging.INFO)

Base = declarative_base()

# ============================================================================
# ORM Models
# ============================================================================

class Product(Base):
    """Product catalog record."""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(150), nullable=False)
    tier = Column(String(50), nullable=False)  # Enterprise, Business, Developer, Addon
    price = Column(Float, nullable=False)
    billing_type = Column(String(50), nullable=False)  # Monthly, Setup Fee, Annual
    description = Column(Text, nullable=False)
    features = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    transactions = relationship("Transaction", back_populates="product")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "product_code": self.product_code,
            "name": self.name,
            "tier": self.tier,
            "price": self.price,
            "billing_type": self.billing_type,
            "description": self.description,
            "features": self.features,
        }


class ClientMaster(Base):
    """Client / Enterprise account master record."""
    __tablename__ = "clients_master"

    id = Column(Integer, primary_key=True, autoincrement=True)
    client_code = Column(String(50), unique=True, nullable=False, index=True)
    company_name = Column(String(150), nullable=False)
    industry = Column(String(100), nullable=False)
    region = Column(String(100), nullable=False)
    tier = Column(String(50), nullable=False)  # Platinum, Gold, Business, Air-Gapped
    contact_person = Column(String(100), nullable=False)
    email = Column(String(120), nullable=False)
    status = Column(String(50), default="Active")  # Active, Onboarding, Review
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    transactions = relationship("Transaction", back_populates="client")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "client_code": self.client_code,
            "company_name": self.company_name,
            "industry": self.industry,
            "region": self.region,
            "tier": self.tier,
            "contact_person": self.contact_person,
            "email": self.email,
            "status": self.status,
        }


class Transaction(Base):
    """Sales, order, and subscription transaction records."""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_ref = Column(String(50), unique=True, nullable=False, index=True)
    client_code = Column(String(50), ForeignKey("clients_master.client_code"), nullable=False)
    product_code = Column(String(50), ForeignKey("products.product_code"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    status = Column(String(50), nullable=False)  # Completed, Pending, Processing
    payment_method = Column(String(50), nullable=False)  # Wire Transfer, ACH, Credit Card
    transaction_date = Column(String(30), nullable=False)
    notes = Column(Text, nullable=True)

    client = relationship("ClientMaster", back_populates="transactions")
    product = relationship("Product", back_populates="transactions")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "transaction_ref": self.transaction_ref,
            "client_code": self.client_code,
            "client_name": self.client.company_name if self.client else self.client_code,
            "product_code": self.product_code,
            "product_name": self.product.name if self.product else self.product_code,
            "amount": self.amount,
            "currency": self.currency,
            "status": self.status,
            "payment_method": self.payment_method,
            "transaction_date": self.transaction_date,
            "notes": self.notes,
        }


# ============================================================================
# Realistic Seed Dataset (5 Products, 5 Masters, 20 Transactions)
# ============================================================================

SAMPLE_PRODUCTS = [
    {
        "product_code": "ND-ENT-01",
        "name": "NexaData Enterprise Engine",
        "tier": "Enterprise Platinum",
        "price": 12500.0,
        "billing_type": "Monthly",
        "description": "Full-stack hybrid RAG, document intelligence, multi-tenant sandboxing, and citation grounding.",
        "features": "Air-gapped deployment, Custom embeddings, 99.99% SLA, Dedicated GPU clusters",
    },
    {
        "product_code": "ND-CLD-02",
        "name": "NexaData Cloud Analytics",
        "tier": "Business",
        "price": 4800.0,
        "billing_type": "Monthly",
        "description": "Managed cloud data warehouse connector with automated BI reporting and interactive SQL querying.",
        "features": "Real-time sync, Snowflake/BigQuery connectors, Row-level security, Automated dashboards",
    },
    {
        "product_code": "ND-SEC-03",
        "name": "NexaData Secure Sandbox",
        "tier": "Security Addon",
        "price": 2200.0,
        "billing_type": "Monthly",
        "description": "Zero-leakage isolated runtime enclave for confidential document processing and PII redaction.",
        "features": "HIPAA/SOC2 compliance, Automated PII masking, Zero data retention, Ephemeral execution",
    },
    {
        "product_code": "ND-API-04",
        "name": "NexaData Inference API Gateway",
        "tier": "Developer",
        "price": 1500.0,
        "billing_type": "Monthly",
        "description": "High-throughput sub-50ms inference gateway with rate management, token caching, and fallback.",
        "features": "Global edge caching, Rate limits per API key, 100k requests/min, Latency routing",
    },
    {
        "product_code": "ND-ETL-05",
        "name": "NexaData Custom ETL Pipeline Suite",
        "tier": "Professional Services",
        "price": 7500.0,
        "billing_type": "One-Time Setup",
        "description": "End-to-end data ingestion engineering for legacy SQL, ERP, CRM, and unstructured PDF sources.",
        "features": "50+ Enterprise connectors, Schema validation, Automatic deduplication, Dedicated data engineer",
    },
]

SAMPLE_MASTERS = [
    {
        "client_code": "MST-101",
        "company_name": "Apex Financial Corp",
        "industry": "Fintech & Banking",
        "region": "North America",
        "tier": "Enterprise Platinum",
        "contact_person": "Sarah Jenkins (VP of Analytics)",
        "email": "s.jenkins@apexfinancial.com",
        "status": "Active",
    },
    {
        "client_code": "MST-102",
        "company_name": "BioGenix Laboratories",
        "industry": "Healthcare & Pharma",
        "region": "Europe",
        "tier": "Enterprise Gold",
        "contact_person": "Dr. Marcus Vance (Head of R&D)",
        "email": "m.vance@biogenix-labs.de",
        "status": "Active",
    },
    {
        "client_code": "MST-103",
        "company_name": "Vertex Logistics Global",
        "industry": "Supply Chain & Freight",
        "region": "Asia-Pacific",
        "tier": "Business",
        "contact_person": "Kenji Tanaka (Operations Director)",
        "email": "k.tanaka@vertexlogistics.jp",
        "status": "Active",
    },
    {
        "client_code": "MST-104",
        "company_name": "OmniRetail Group",
        "industry": "E-Commerce & Retail",
        "region": "North America",
        "tier": "Enterprise Platinum",
        "contact_person": "Rachel Torres (Chief Technology Officer)",
        "email": "r.torres@omniretail.com",
        "status": "Active",
    },
    {
        "client_code": "MST-105",
        "company_name": "CyberShield Dynamics",
        "industry": "Defense & Cyber",
        "region": "Europe",
        "tier": "Enterprise Air-Gapped",
        "contact_person": "Alexey Morozov (Chief Information Security Officer)",
        "email": "a.morozov@cybershield.eu",
        "status": "Active",
    },
]

SAMPLE_TRANSACTIONS = [
    {"transaction_ref": "TXN-2024-001", "client_code": "MST-101", "product_code": "ND-ENT-01", "amount": 12500.0, "currency": "USD", "status": "Completed", "payment_method": "Wire Transfer", "transaction_date": "2024-09-01", "notes": "Monthly Enterprise license renewal"},
    {"transaction_ref": "TXN-2024-002", "client_code": "MST-101", "product_code": "ND-SEC-03", "amount": 2200.0, "currency": "USD", "status": "Completed", "payment_method": "Wire Transfer", "transaction_date": "2024-09-01", "notes": "Zero-leakage sandbox add-on"},
    {"transaction_ref": "TXN-2024-003", "client_code": "MST-102", "product_code": "ND-ENT-01", "amount": 12500.0, "currency": "USD", "status": "Completed", "payment_method": "ACH", "transaction_date": "2024-09-05", "notes": "European pharma clinical trial RAG"},
    {"transaction_ref": "TXN-2024-004", "client_code": "MST-103", "product_code": "ND-CLD-02", "amount": 4800.0, "currency": "USD", "status": "Completed", "payment_method": "Credit Card", "transaction_date": "2024-09-08", "notes": "APAC freight tracking analytics"},
    {"transaction_ref": "TXN-2024-005", "client_code": "MST-104", "product_code": "ND-ENT-01", "amount": 12500.0, "currency": "USD", "status": "Completed", "payment_method": "Corporate ACH", "transaction_date": "2024-09-12", "notes": "E-Commerce recommendation intelligence"},
    {"transaction_ref": "TXN-2024-006", "client_code": "MST-104", "product_code": "ND-ETL-05", "amount": 7500.0, "currency": "USD", "status": "Completed", "payment_method": "Corporate ACH", "transaction_date": "2024-09-15", "notes": "Shopify & ERP ingestion setup"},
    {"transaction_ref": "TXN-2024-007", "client_code": "MST-105", "product_code": "ND-ENT-01", "amount": 12500.0, "currency": "USD", "status": "Completed", "payment_method": "Wire Transfer", "transaction_date": "2024-09-18", "notes": "Air-gapped on-premise cluster"},
    {"transaction_ref": "TXN-2024-008", "client_code": "MST-105", "product_code": "ND-SEC-03", "amount": 2200.0, "currency": "USD", "status": "Completed", "payment_method": "Wire Transfer", "transaction_date": "2024-09-18", "notes": "Security sandbox extension"},
    {"transaction_ref": "TXN-2024-009", "client_code": "MST-102", "product_code": "ND-API-04", "amount": 1500.0, "currency": "USD", "status": "Completed", "payment_method": "Credit Card", "transaction_date": "2024-09-22", "notes": "Laboratory edge API gateway"},
    {"transaction_ref": "TXN-2024-010", "client_code": "MST-103", "product_code": "ND-ETL-05", "amount": 7500.0, "currency": "USD", "status": "Completed", "payment_method": "ACH", "transaction_date": "2024-09-25", "notes": "Port container telemetry pipelines"},
    {"transaction_ref": "TXN-2024-011", "client_code": "MST-101", "product_code": "ND-ENT-01", "amount": 12500.0, "currency": "USD", "status": "Completed", "payment_method": "Wire Transfer", "transaction_date": "2024-10-01", "notes": "October monthly license renewal"},
    {"transaction_ref": "TXN-2024-012", "client_code": "MST-101", "product_code": "ND-SEC-03", "amount": 2200.0, "currency": "USD", "status": "Completed", "payment_method": "Wire Transfer", "transaction_date": "2024-10-01", "notes": "October sandbox add-on"},
    {"transaction_ref": "TXN-2024-013", "client_code": "MST-102", "product_code": "ND-ENT-01", "amount": 12500.0, "currency": "USD", "status": "Completed", "payment_method": "ACH", "transaction_date": "2024-10-05", "notes": "October monthly renewal"},
    {"transaction_ref": "TXN-2024-014", "client_code": "MST-103", "product_code": "ND-CLD-02", "amount": 4800.0, "currency": "USD", "status": "Completed", "payment_method": "Credit Card", "transaction_date": "2024-10-08", "notes": "October cloud analytics"},
    {"transaction_ref": "TXN-2024-015", "client_code": "MST-104", "product_code": "ND-ENT-01", "amount": 12500.0, "currency": "USD", "status": "Completed", "payment_method": "Corporate ACH", "transaction_date": "2024-10-10", "notes": "October enterprise license"},
    {"transaction_ref": "TXN-2024-016", "client_code": "MST-104", "product_code": "ND-API-04", "amount": 1500.0, "currency": "USD", "status": "Completed", "payment_method": "Credit Card", "transaction_date": "2024-10-11", "notes": "Peak season inference API burst tier"},
    {"transaction_ref": "TXN-2024-017", "client_code": "MST-105", "product_code": "ND-ENT-01", "amount": 12500.0, "currency": "USD", "status": "Pending", "payment_method": "Wire Transfer", "transaction_date": "2024-10-12", "notes": "October defense contract clearance"},
    {"transaction_ref": "TXN-2024-018", "client_code": "MST-101", "product_code": "ND-API-04", "amount": 1500.0, "currency": "USD", "status": "Completed", "payment_method": "Credit Card", "transaction_date": "2024-10-12", "notes": "High frequency fraud query gateway"},
    {"transaction_ref": "TXN-2024-019", "client_code": "MST-102", "product_code": "ND-ETL-05", "amount": 7500.0, "currency": "USD", "status": "Processing", "payment_method": "ACH", "transaction_date": "2024-10-13", "notes": "Genomics lab equipment telemetry setup"},
    {"transaction_ref": "TXN-2024-020", "client_code": "MST-103", "product_code": "ND-API-04", "amount": 1500.0, "currency": "USD", "status": "Pending", "payment_method": "Credit Card", "transaction_date": "2024-10-13", "notes": "Driver mobile app query integration"},
]


# ============================================================================
# Database Engine Manager
# ============================================================================

class DatabaseEngine:
    """Manages connection, schema creation, fallback, and seeding."""

    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.db_type = "uninitialized"
        self.connection_string = ""
        self.init_database()

    def _build_connection_string(self) -> tuple[str, str]:
        """Determine connection string from environment."""
        # 1. Direct DATABASE_URL (Heroku/Render standard)
        db_url = os.getenv("DATABASE_URL")
        if db_url:
            # Handle postgres:// vs postgresql://
            if db_url.startswith("postgres://"):
                db_url = db_url.replace("postgres://", "postgresql://", 1)
            return db_url, "postgresql"

        # 2. Discrete POSTGRES_* environment variables
        host = os.getenv("POSTGRES_HOST")
        user = os.getenv("POSTGRES_USER", "postgres")
        password = os.getenv("POSTGRES_PASSWORD", "")
        port = os.getenv("POSTGRES_PORT", "5432")
        db = os.getenv("POSTGRES_DB", "nexadata_db")

        if host:
            auth = f"{user}:{password}@" if password else f"{user}@"
            conn = f"postgresql://{auth}{host}:{port}/{db}"
            return conn, "postgresql"

        # 3. Fallback to local SQLite mirror
        data_dir = Path(__file__).resolve().parent.parent / "data"
        data_dir.mkdir(exist_ok=True)
        sqlite_path = data_dir / "nexadata.db"
        return f"sqlite:///{sqlite_path}", "sqlite"

    def init_database(self):
        """Initialize connection, tables, and seed dataset."""
        conn_str, db_type = self._build_connection_string()
        self.db_type = db_type
        self.connection_string = conn_str

        try:
            if db_type == "postgresql":
                # Test postgres connection with timeout
                self.engine = create_engine(
                    conn_str,
                    pool_pre_ping=True,
                    connect_args={"connect_timeout": 3}
                )
                with self.engine.connect() as conn:
                    pass  # Verified connection
                logger.info("Connected to PostgreSQL successfully.")
            else:
                self.engine = create_engine(conn_str, connect_args={"check_same_thread": False})
                logger.info(f"Using SQLite database engine at {conn_str}")
        except Exception as e:
            logger.warning(f"Failed to connect to PostgreSQL ({e}). Falling back to SQLite mirror.")
            data_dir = Path(__file__).resolve().parent.parent / "data"
            data_dir.mkdir(exist_ok=True)
            fallback_conn = f"sqlite:///{data_dir / 'nexadata.db'}"
            self.engine = create_engine(fallback_conn, connect_args={"check_same_thread": False})
            self.db_type = "sqlite (fallback)"
            self.connection_string = fallback_conn

        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

        # Create schema tables
        Base.metadata.create_all(bind=self.engine)

        # Pre-seed records if empty
        self.seed_sample_data()

    def get_session(self):
        """Provide a scoped session."""
        if not self.SessionLocal:
            self.init_database()
        return self.SessionLocal()

    def seed_sample_data(self):
        """Seed 5 products, 5 client masters, and 20 transactions if not present."""
        session = self.get_session()
        try:
            # 1. Products
            p_count = session.query(Product).count()
            if p_count == 0:
                for p in SAMPLE_PRODUCTS:
                    session.add(Product(**p))
                session.commit()
                logger.info("Seeded 5 Product catalog records.")

            # 2. Master Records
            m_count = session.query(ClientMaster).count()
            if m_count == 0:
                for m in SAMPLE_MASTERS:
                    session.add(ClientMaster(**m))
                session.commit()
                logger.info("Seeded 5 Client Master accounts.")

            # 3. Transactions
            t_count = session.query(Transaction).count()
            if t_count == 0:
                for t in SAMPLE_TRANSACTIONS:
                    session.add(Transaction(**t))
                session.commit()
                logger.info("Seeded 20 Business Transactions.")
        except Exception as e:
            session.rollback()
            logger.error(f"Error seeding sample dataset: {e}")
        finally:
            session.close()


db_engine = DatabaseEngine()


# ============================================================================
# Data Access & Retrieval Functions
# ============================================================================

def get_products_list() -> List[Dict[str, Any]]:
    """Retrieve all product records."""
    session = db_engine.get_session()
    try:
        products = session.query(Product).all()
        return [p.to_dict() for p in products]
    finally:
        session.close()


def get_master_records_list() -> List[Dict[str, Any]]:
    """Retrieve all client master records."""
    session = db_engine.get_session()
    try:
        clients = session.query(ClientMaster).all()
        return [c.to_dict() for c in clients]
    finally:
        session.close()


def get_transactions_list(limit: int = 50, client_code: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve transaction records with optional filters."""
    session = db_engine.get_session()
    try:
        query = session.query(Transaction)
        if client_code:
            query = query.filter(Transaction.client_code == client_code)
        if status:
            query = query.filter(Transaction.status == status)
        txns = query.order_by(Transaction.id.asc()).limit(limit).all()
        return [t.to_dict() for t in txns]
    finally:
        session.close()


def get_analytics_summary() -> Dict[str, Any]:
    """Retrieve high-level business analytics summary."""
    session = db_engine.get_session()
    try:
        products = session.query(Product).all()
        clients = session.query(ClientMaster).all()
        txns = session.query(Transaction).all()

        total_revenue = sum(t.amount for t in txns if t.status == "Completed")
        pending_revenue = sum(t.amount for t in txns if t.status != "Completed")

        return {
            "database_engine": db_engine.db_type,
            "total_products": len(products),
            "total_clients": len(clients),
            "total_transactions": len(txns),
            "completed_transactions": len([t for t in txns if t.status == "Completed"]),
            "pending_transactions": len([t for t in txns if t.status != "Completed"]),
            "total_revenue_usd": total_revenue,
            "pending_revenue_usd": pending_revenue,
        }
    finally:
        session.close()


def search_records(query_str: str) -> Dict[str, Any]:
    """Search across products, client masters, and transactions."""
    session = db_engine.get_session()
    q = f"%{query_str.lower()}%"
    try:
        p_matches = session.query(Product).filter(
            (Product.name.ilike(q)) | (Product.product_code.ilike(q)) | (Product.tier.ilike(q))
        ).all()

        c_matches = session.query(ClientMaster).filter(
            (ClientMaster.company_name.ilike(q)) | (ClientMaster.client_code.ilike(q)) | (ClientMaster.industry.ilike(q))
        ).all()

        t_matches = session.query(Transaction).filter(
            (Transaction.transaction_ref.ilike(q)) | (Transaction.client_code.ilike(q)) | (Transaction.product_code.ilike(q))
        ).all()

        return {
            "products": [p.to_dict() for p in p_matches],
            "clients": [c.to_dict() for c in c_matches],
            "transactions": [t.to_dict() for t in t_matches],
        }
    finally:
        session.close()


def query_database_smart(prompt: str) -> Optional[str]:
    """Inspect user query and return formatted markdown tables if relevant to DB."""
    p_lower = prompt.lower()

    # Keywords for DB triggers
    is_product_query = any(k in p_lower for k in ["product", "catalog", "offer", "pricing", "tier", "features"])
    is_client_query = any(k in p_lower for k in ["client", "master record", "master account", "customer", "apex financial", "biogenix", "vertex logistics", "omniretail", "cybershield"])
    is_txn_query = any(k in p_lower for k in ["transaction", "invoice", "order", "sales", "revenue", "payment", "txn-"])
    is_db_summary = any(k in p_lower for k in ["database summary", "database stats", "records in database", "how many records"])

    if not (is_product_query or is_client_query or is_txn_query or is_db_summary):
        return None

    response_parts = []

    # 1. DB Summary
    if is_db_summary or ("database" in p_lower and "show" in p_lower):
        stats = get_analytics_summary()
        response_parts.append(
            f"### 🗄️ NexaData Enterprise Database Status\n"
            f"- **Engine**: `{stats['database_engine'].upper()}`\n"
            f"- **Product Records**: {stats['total_products']}\n"
            f"- **Client Master Accounts**: {stats['total_clients']}\n"
            f"- **Total Transactions**: {stats['total_transactions']} ({stats['completed_transactions']} Completed, {stats['pending_transactions']} Pending)\n"
            f"- **Total Recognized Revenue**: **${stats['total_revenue_usd']:,.2f} USD**\n"
        )

    # 2. Products
    if is_product_query:
        products = get_products_list()
        table_rows = [
            "| Code | Product Name | Tier | Price | Billing | Description |",
            "| :--- | :--- | :--- | :--- | :--- | :--- |"
        ]
        for p in products:
            table_rows.append(f"| `{p['product_code']}` | **{p['name']}** | {p['tier']} | ${p['price']:,.2f} | {p['billing_type']} | {p['description']} |")

        response_parts.append(
            "### 📦 Official NexaData Product Catalog (Database Records)\n\n" +
            "\n".join(table_rows)
        )

    # 3. Clients Master
    if is_client_query:
        clients = get_master_records_list()
        table_rows = [
            "| Client ID | Company Name | Industry | Region | Tier | Contact Person | Status |",
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
        ]
        for c in clients:
            table_rows.append(f"| `{c['client_code']}` | **{c['company_name']}** | {c['industry']} | {c['region']} | {c['tier']} | {c['contact_person']} | `{c['status']}` |")

        response_parts.append(
            "### 🏢 Client Master Accounts (Database Records)\n\n" +
            "\n".join(table_rows)
        )

    # 4. Transactions
    if is_txn_query:
        # Check if query targets a specific client
        matched_client = None
        for code, name in [
            ("MST-101", "apex"), ("MST-102", "biogenix"),
            ("MST-103", "vertex"), ("MST-104", "omni"), ("MST-105", "cyber")
        ]:
            if name in p_lower:
                matched_client = code
                break

        txns = get_transactions_list(limit=20, client_code=matched_client)
        table_rows = [
            "| Reference | Client | Product | Amount | Status | Method | Date | Notes |",
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
        ]
        for t in txns:
            status_badge = f"✅ {t['status']}" if t['status'] == 'Completed' else f"⏳ {t['status']}"
            table_rows.append(f"| `{t['transaction_ref']}` | **{t['client_name']}** | `{t['product_code']}` | ${t['amount']:,.2f} | {status_badge} | {t['payment_method']} | {t['transaction_date']} | {t['notes']} |")

        header = f"### 💳 Enterprise Transactions ({len(txns)} Records)"
        if matched_client:
            header += f" for Client `{matched_client}`"

        response_parts.append(header + "\n\n" + "\n".join(table_rows))

    if response_parts:
        return "\n\n---\n\n".join(response_parts)
    return None
