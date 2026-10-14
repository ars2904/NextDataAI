"""PostgreSQL Database Engine & Data Access Layer for NexaData AI.

Supports standard PostgreSQL via DATABASE_URL or discrete POSTGRES_* environment variables.
Provides automatic, zero-crash fallback to local SQLite for environments where a live
PostgreSQL daemon is not locally running.

Relational schema covers 14 business areas:
- Company Information
- Departments
- Employees
- Product Categories
- Suppliers
- Products (24 records >= 20)
- Inventory Records (24 records)
- Customer Accounts (55 records >= 50)
- Clients Master (5 compatible accounts)
- Orders (115 records >= 100)
- Order Line Items (260+ records)
- Payments (115 records)
- Sales & Subscription Transactions (215 records >= 200)
- Corporate Policies (10 records)
- FAQs (15 records)
"""
import os
import sys
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

from database.seed_builder import (
    COMPANY_INFO_DATA,
    DEPARTMENTS_DATA,
    EMPLOYEES_DATA,
    CATEGORIES_DATA,
    SUPPLIERS_DATA,
    PRODUCTS_DATA,
    INVENTORY_DATA,
    CUSTOMERS_DATA,
    CLIENTS_MASTER_DATA,
    ORDERS_DATA,
    ORDER_ITEMS_DATA,
    PAYMENTS_DATA,
    TRANSACTIONS_DATA,
    POLICIES_DATA,
    FAQS_DATA,
    ORIGINAL_20_TRANSACTIONS,
)

logger = logging.getLogger("nexadata.database")
logger.setLevel(logging.INFO)

Base = declarative_base()

# ============================================================================
# ORM Models (15 Relational Entities)
# ============================================================================

class CompanyInfo(Base):
    """Company profile and legal entity metadata."""
    __tablename__ = "company_info"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String(150), nullable=False)
    legal_name = Column(String(150), nullable=False)
    tagline = Column(String(255), nullable=False)
    tax_id = Column(String(50), nullable=True)
    founded_year = Column(Integer, nullable=False)
    headquarters = Column(String(255), nullable=False)
    website = Column(String(120), nullable=False)
    support_email = Column(String(120), nullable=False)
    sales_email = Column(String(120), nullable=False)
    phone = Column(String(50), nullable=False)
    mission = Column(Text, nullable=False)
    vision = Column(Text, nullable=False)
    fiscal_year_end = Column(String(30), default="December 31")
    primary_currency = Column(String(10), default="USD")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "company_name": self.company_name,
            "legal_name": self.legal_name,
            "tagline": self.tagline,
            "tax_id": self.tax_id,
            "founded_year": self.founded_year,
            "headquarters": self.headquarters,
            "website": self.website,
            "support_email": self.support_email,
            "sales_email": self.sales_email,
            "phone": self.phone,
            "mission": self.mission,
            "vision": self.vision,
            "fiscal_year_end": self.fiscal_year_end,
            "primary_currency": self.primary_currency,
        }


class Department(Base):
    """Corporate business departments and budget allocations."""
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    department_code = Column(String(30), unique=True, nullable=False, index=True)
    name = Column(String(120), nullable=False)
    head_of_department = Column(String(120), nullable=False)
    budget = Column(Float, nullable=False)
    location = Column(String(120), nullable=False)
    employee_count = Column(Integer, default=0)
    contact_email = Column(String(120), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "department_code": self.department_code,
            "name": self.name,
            "head_of_department": self.head_of_department,
            "budget": self.budget,
            "location": self.location,
            "employee_count": self.employee_count,
            "contact_email": self.contact_email,
        }


class Employee(Base):
    """Staff and key personnel directory."""
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_code = Column(String(30), unique=True, nullable=False, index=True)
    first_name = Column(String(60), nullable=False)
    last_name = Column(String(60), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    phone = Column(String(30), nullable=True)
    department_code = Column(String(30), nullable=False)
    role = Column(String(120), nullable=False)
    salary = Column(Float, nullable=False)
    hire_date = Column(String(30), nullable=False)
    status = Column(String(30), default="Active")
    location = Column(String(120), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "employee_code": self.employee_code,
            "full_name": f"{self.first_name} {self.last_name}",
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "department_code": self.department_code,
            "role": self.role,
            "salary": self.salary,
            "hire_date": self.hire_date,
            "status": self.status,
            "location": self.location,
        }


class Category(Base):
    """Product and solution taxonomy categories."""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_code = Column(String(30), unique=True, nullable=False, index=True)
    name = Column(String(120), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "category_code": self.category_code,
            "name": self.name,
            "description": self.description,
        }


class Supplier(Base):
    """Infrastructure partners, cloud providers, and hardware vendors."""
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    supplier_code = Column(String(30), unique=True, nullable=False, index=True)
    name = Column(String(150), nullable=False)
    contact_name = Column(String(100), nullable=False)
    email = Column(String(120), nullable=False)
    phone = Column(String(30), nullable=True)
    country = Column(String(60), nullable=False)
    service_type = Column(String(120), nullable=False)
    rating = Column(Float, default=5.0)
    payment_terms = Column(String(50), default="Net 30")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "supplier_code": self.supplier_code,
            "name": self.name,
            "contact_name": self.contact_name,
            "email": self.email,
            "country": self.country,
            "service_type": self.service_type,
            "rating": self.rating,
            "payment_terms": self.payment_terms,
        }


class Product(Base):
    """Product catalog record (24 products across all tiers)."""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(150), nullable=False)
    tier = Column(String(50), nullable=False)
    category_code = Column(String(30), nullable=True)
    supplier_code = Column(String(30), nullable=True)
    price = Column(Float, nullable=False)
    cost_price = Column(Float, default=0.0)
    billing_type = Column(String(50), nullable=False)
    stock_quantity = Column(Integer, default=100)
    description = Column(Text, nullable=False)
    features = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "product_code": self.product_code,
            "name": self.name,
            "tier": self.tier,
            "category_code": self.category_code,
            "price": self.price,
            "cost_price": self.cost_price,
            "billing_type": self.billing_type,
            "stock_quantity": self.stock_quantity,
            "description": self.description,
            "features": self.features,
            "is_active": self.is_active,
        }


class Inventory(Base):
    """Inventory levels, warehouse clusters, and reorder alerts."""
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sku = Column(String(60), unique=True, nullable=False, index=True)
    product_code = Column(String(50), nullable=False, index=True)
    warehouse_location = Column(String(120), nullable=False)
    quantity_available = Column(Integer, nullable=False, default=0)
    quantity_reserved = Column(Integer, nullable=False, default=0)
    reorder_level = Column(Integer, nullable=False, default=10)
    unit_cost = Column(Float, nullable=False)
    status = Column(String(40), default="In Stock")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "sku": self.sku,
            "product_code": self.product_code,
            "warehouse_location": self.warehouse_location,
            "quantity_available": self.quantity_available,
            "quantity_reserved": self.quantity_reserved,
            "reorder_level": self.reorder_level,
            "unit_cost": self.unit_cost,
            "status": self.status,
        }


class Customer(Base):
    """Customer enterprise accounts (55 accounts across industries)."""
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_code = Column(String(50), unique=True, nullable=False, index=True)
    company_name = Column(String(150), nullable=False)
    contact_name = Column(String(100), nullable=False)
    email = Column(String(120), nullable=False)
    phone = Column(String(40), nullable=True)
    city = Column(String(80), nullable=False)
    state = Column(String(80), nullable=True)
    country = Column(String(80), nullable=False)
    industry = Column(String(100), nullable=False)
    tier = Column(String(50), default="Standard")
    credit_limit = Column(Float, default=50000.0)
    account_balance = Column(Float, default=0.0)
    sales_rep_code = Column(String(30), nullable=True)
    status = Column(String(40), default="Active")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "customer_code": self.customer_code,
            "company_name": self.company_name,
            "contact_name": self.contact_name,
            "email": self.email,
            "phone": self.phone,
            "city": self.city,
            "state": self.state,
            "country": self.country,
            "industry": self.industry,
            "tier": self.tier,
            "credit_limit": self.credit_limit,
            "account_balance": self.account_balance,
            "sales_rep_code": self.sales_rep_code,
            "status": self.status,
        }


class ClientMaster(Base):
    """Client Master record (Preserved for backwards compatibility with existing tests)."""
    __tablename__ = "clients_master"

    id = Column(Integer, primary_key=True, autoincrement=True)
    client_code = Column(String(50), unique=True, nullable=False, index=True)
    company_name = Column(String(150), nullable=False)
    industry = Column(String(100), nullable=False)
    region = Column(String(100), nullable=False)
    tier = Column(String(50), nullable=False)
    contact_person = Column(String(100), nullable=False)
    email = Column(String(120), nullable=False)
    status = Column(String(50), default="Active")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

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


class Order(Base):
    """Customer purchase orders and subscription renewals (115 orders)."""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_number = Column(String(60), unique=True, nullable=False, index=True)
    customer_code = Column(String(50), nullable=False, index=True)
    order_date = Column(String(30), nullable=False)
    status = Column(String(40), default="Completed")
    total_amount = Column(Float, nullable=False)
    discount_amount = Column(Float, default=0.0)
    net_amount = Column(Float, nullable=False)
    payment_status = Column(String(40), default="Paid")
    sales_rep_code = Column(String(30), nullable=True)
    billing_cycle = Column(String(40), default="Monthly")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "order_number": self.order_number,
            "customer_code": self.customer_code,
            "order_date": self.order_date,
            "status": self.status,
            "total_amount": self.total_amount,
            "discount_amount": self.discount_amount,
            "net_amount": self.net_amount,
            "payment_status": self.payment_status,
            "sales_rep_code": self.sales_rep_code,
            "billing_cycle": self.billing_cycle,
            "notes": self.notes,
        }


class OrderItem(Base):
    """Line items for orders."""
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_number = Column(String(60), nullable=False, index=True)
    product_code = Column(String(50), nullable=False, index=True)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    discount = Column(Float, default=0.0)
    line_total = Column(Float, nullable=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "order_number": self.order_number,
            "product_code": self.product_code,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "subtotal": self.subtotal,
            "discount": self.discount,
            "line_total": self.line_total,
        }


class Payment(Base):
    """Payment records for orders."""
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    payment_ref = Column(String(60), unique=True, nullable=False, index=True)
    order_number = Column(String(60), nullable=False, index=True)
    customer_code = Column(String(50), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    payment_method = Column(String(50), nullable=False)
    status = Column(String(40), default="Success")
    payment_date = Column(String(30), nullable=False)
    gateway_ref = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "payment_ref": self.payment_ref,
            "order_number": self.order_number,
            "customer_code": self.customer_code,
            "amount": self.amount,
            "currency": self.currency,
            "payment_method": self.payment_method,
            "status": self.status,
            "payment_date": self.payment_date,
            "gateway_ref": self.gateway_ref,
        }


class Transaction(Base):
    """Sales, order, and subscription transaction records (215 transactions)."""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_ref = Column(String(60), unique=True, nullable=False, index=True)
    client_code = Column(String(50), nullable=False, index=True)
    product_code = Column(String(50), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    status = Column(String(50), nullable=False)  # Completed, Pending, Processing
    payment_method = Column(String(50), nullable=False)
    transaction_date = Column(String(40), nullable=False)
    notes = Column(Text, nullable=True)

    def to_dict(self, client_name_map: Optional[Dict[str, str]] = None, product_name_map: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        c_name = self.client_code
        if client_name_map and self.client_code in client_name_map:
            c_name = client_name_map[self.client_code]
        
        p_name = self.product_code
        if product_name_map and self.product_code in product_name_map:
            p_name = product_name_map[self.product_code]

        return {
            "id": self.id,
            "transaction_ref": self.transaction_ref,
            "client_code": self.client_code,
            "client_name": c_name,
            "product_code": self.product_code,
            "product_name": p_name,
            "amount": self.amount,
            "currency": self.currency,
            "status": self.status,
            "payment_method": self.payment_method,
            "transaction_date": self.transaction_date,
            "notes": self.notes,
        }


class Policy(Base):
    """Corporate governance, data privacy, and SLA policies (10 policies)."""
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    policy_code = Column(String(40), unique=True, nullable=False, index=True)
    title = Column(String(160), nullable=False)
    category = Column(String(60), nullable=False)
    version = Column(String(20), default="v1.0")
    effective_date = Column(String(30), nullable=False)
    department_code = Column(String(30), nullable=True)
    summary = Column(Text, nullable=False)
    full_text = Column(Text, nullable=False)
    status = Column(String(30), default="Active")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "policy_code": self.policy_code,
            "title": self.title,
            "category": self.category,
            "version": self.version,
            "effective_date": self.effective_date,
            "department_code": self.department_code,
            "summary": self.summary,
            "full_text": self.full_text,
            "status": self.status,
        }


class FAQ(Base):
    """Corporate and technical FAQs (15 items)."""
    __tablename__ = "faqs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    faq_code = Column(String(40), unique=True, nullable=False, index=True)
    category = Column(String(60), nullable=False)
    question = Column(String(255), nullable=False)
    answer = Column(Text, nullable=False)
    keywords = Column(String(255), nullable=True)
    is_published = Column(Boolean, default=True)
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "faq_code": self.faq_code,
            "category": self.category,
            "question": self.question,
            "answer": self.answer,
            "keywords": self.keywords,
            "is_published": self.is_published,
            "view_count": self.view_count,
        }


class User(Base):
    """User accounts for multi-tenant isolation and session management."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(120), nullable=False)
    role = Column(String(40), default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_login_at = Column(DateTime, nullable=True)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
        }


class ChatSession(Base):
    """Server-side persistent chat sessions for cross-device sync."""
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(80), unique=True, nullable=False, index=True)
    user_id = Column(String(80), nullable=True, index=True)
    title = Column(String(200), nullable=False)
    mode = Column(String(40), default="company")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.session_id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "title": self.title,
            "mode": self.mode,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ChatMessage(Base):
    """Persistent chat messages belonging to a chat session."""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(80), nullable=False, index=True)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    sources_json = Column(Text, nullable=True)
    timestamp = Column(String(40), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        import json
        sources = []
        if self.sources_json:
            try:
                sources = json.loads(self.sources_json)
            except Exception:
                sources = []
        return {
            "id": self.id,
            "session_id": self.session_id,
            "role": self.role,
            "type": "user" if self.role == "user" else "bot",
            "text": self.content if self.role == "user" else None,
            "reply": self.content if self.role != "user" else None,
            "sources": sources,
            "timestamp": self.timestamp,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# Backwards compatibility aliases
SAMPLE_PRODUCTS = PRODUCTS_DATA[:5]
SAMPLE_MASTERS = CLIENTS_MASTER_DATA
SAMPLE_TRANSACTIONS = ORIGINAL_20_TRANSACTIONS


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

        # Migration: Ensure user_id column exists on chat_sessions for backward compatibility
        try:
            with self.engine.connect() as conn:
                from sqlalchemy import text
                conn.execute(text("ALTER TABLE chat_sessions ADD COLUMN user_id VARCHAR(80)"))
                conn.commit()
        except Exception:
            pass  # Column already exists or table freshly created

        # Pre-seed records if empty
        self.seed_sample_data()


    def get_session(self):
        """Provide a scoped session."""
        if not self.SessionLocal:
            self.init_database()
        return self.SessionLocal()

    def connect(self):
        """Provide direct connection to underlying SQLAlchemy engine."""
        if not self.engine:
            self.init_database()
        return self.engine.connect()

    def seed_sample_data(self):
        """Seed all 14 business areas if records are not present."""
        session = self.get_session()
        try:
            # 1. Company Info
            if session.query(CompanyInfo).count() == 0:
                session.add(CompanyInfo(**COMPANY_INFO_DATA))
                session.commit()
                logger.info("Seeded Company Information.")

            # 2. Departments
            if session.query(Department).count() == 0:
                for d in DEPARTMENTS_DATA:
                    session.add(Department(**d))
                session.commit()
                logger.info("Seeded 7 Corporate Departments.")

            # 3. Employees
            if session.query(Employee).count() == 0:
                for emp in EMPLOYEES_DATA:
                    session.add(Employee(**emp))
                session.commit()
                logger.info("Seeded 25 Employees.")

            # 4. Product Categories
            if session.query(Category).count() == 0:
                for c in CATEGORIES_DATA:
                    session.add(Category(**c))
                session.commit()
                logger.info("Seeded 8 Categories.")

            # 5. Suppliers
            if session.query(Supplier).count() == 0:
                for s in SUPPLIERS_DATA:
                    session.add(Supplier(**s))
                session.commit()
                logger.info("Seeded 10 Suppliers.")

            # 6. Products (24 records >= 20)
            if session.query(Product).count() == 0:
                for p in PRODUCTS_DATA:
                    session.add(Product(**p))
                session.commit()
                logger.info("Seeded 24 Products.")

            # 7. Inventory (24 records)
            if session.query(Inventory).count() == 0:
                for inv in INVENTORY_DATA:
                    session.add(Inventory(
                        sku=inv["sku"],
                        product_code=inv["product_code"],
                        warehouse_location=inv["location"],
                        quantity_available=inv["available"],
                        quantity_reserved=inv["reserved"],
                        reorder_level=inv["reorder"],
                        unit_cost=inv["unit_cost"],
                        status=inv["status"]
                    ))
                session.commit()
                logger.info("Seeded 24 Inventory Records.")

            # 8. Customers (55 records >= 50)
            if session.query(Customer).count() == 0:
                for cust in CUSTOMERS_DATA:
                    session.add(Customer(**cust))
                session.commit()
                logger.info("Seeded 55 Customer Accounts.")

            # 9. Clients Master (5 compatible accounts)
            if session.query(ClientMaster).count() == 0:
                for m in CLIENTS_MASTER_DATA:
                    session.add(ClientMaster(**m))
                session.commit()
                logger.info("Seeded 5 Client Master Accounts.")

            # 10. Orders (115 records >= 100)
            if session.query(Order).count() == 0:
                for o in ORDERS_DATA:
                    session.add(Order(**o))
                session.commit()
                logger.info("Seeded 115 Orders.")

            # 11. Order Items (260+ records)
            if session.query(OrderItem).count() == 0:
                for item in ORDER_ITEMS_DATA:
                    session.add(OrderItem(**item))
                session.commit()
                logger.info("Seeded Order Line Items.")

            # 12. Payments (115 records)
            if session.query(Payment).count() == 0:
                for pay in PAYMENTS_DATA:
                    session.add(Payment(**pay))
                session.commit()
                logger.info("Seeded 115 Payments.")

            # 13. Transactions (215 records >= 200)
            if session.query(Transaction).count() == 0:
                for t in TRANSACTIONS_DATA:
                    session.add(Transaction(**t))
                session.commit()
                logger.info("Seeded 215 Business Transactions.")

            # 14. Policies (10 corporate policies)
            if session.query(Policy).count() == 0:
                for pol in POLICIES_DATA:
                    session.add(Policy(**pol))
                session.commit()
                logger.info("Seeded 10 Corporate Policies.")

            # 15. FAQs (15 FAQs)
            if session.query(FAQ).count() == 0:
                for faq in FAQS_DATA:
                    session.add(FAQ(**faq))
                session.commit()
                logger.info("Seeded 15 Corporate FAQs.")

            # 16. Default User Accounts (Option B Hybrid Mode Demo & Admin)
            if session.query(User).count() == 0:
                from backend.security import hash_password
                admin_user = User(
                    user_id="user_admin_001",
                    email="admin@nexadata.ai",
                    password_hash=hash_password("NexaData2026!"),
                    full_name="System Administrator",
                    role="admin",
                    is_active=True
                )
                demo_user = User(
                    user_id="user_demo_002",
                    email="demo@nexadata.ai",
                    password_hash=hash_password("NexaDemo2026!"),
                    full_name="Demo Analyst",
                    role="user",
                    is_active=True
                )
                session.add_all([admin_user, demo_user])
                session.commit()
                logger.info("Seeded default Admin and Demo user accounts.")

        except Exception as e:
            session.rollback()
            logger.error(f"Error seeding database records: {e}")
        finally:
            session.close()


db_engine = DatabaseEngine()


# ============================================================================
# Data Access & Retrieval Functions
# ============================================================================

def get_company_info() -> Optional[Dict[str, Any]]:
    """Retrieve official company info record."""
    session = db_engine.get_session()
    try:
        record = session.query(CompanyInfo).first()
        return record.to_dict() if record else None
    finally:
        session.close()


def get_departments_list() -> List[Dict[str, Any]]:
    """Retrieve all corporate departments."""
    session = db_engine.get_session()
    try:
        deps = session.query(Department).order_by(Department.id.asc()).all()
        return [d.to_dict() for d in deps]
    finally:
        session.close()


def get_employees_list(limit: int = 50, department_code: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve staff employees with optional department filter."""
    session = db_engine.get_session()
    try:
        query = session.query(Employee)
        if department_code:
            query = query.filter(Employee.department_code == department_code)
        employees = query.order_by(Employee.id.asc()).limit(limit).all()
        return [e.to_dict() for e in employees]
    finally:
        session.close()


def get_categories_list() -> List[Dict[str, Any]]:
    """Retrieve all product categories."""
    session = db_engine.get_session()
    try:
        cats = session.query(Category).order_by(Category.id.asc()).all()
        return [c.to_dict() for c in cats]
    finally:
        session.close()


def get_suppliers_list() -> List[Dict[str, Any]]:
    """Retrieve all suppliers and hardware vendors."""
    session = db_engine.get_session()
    try:
        sups = session.query(Supplier).order_by(Supplier.id.asc()).all()
        return [s.to_dict() for s in sups]
    finally:
        session.close()


def get_products_list() -> List[Dict[str, Any]]:
    """Retrieve all product catalog records (24 records)."""
    session = db_engine.get_session()
    try:
        products = session.query(Product).order_by(Product.id.asc()).all()
        return [p.to_dict() for p in products]
    finally:
        session.close()


def get_inventory_list(limit: int = 50, low_stock_only: bool = False) -> List[Dict[str, Any]]:
    """Retrieve inventory levels across warehouses."""
    session = db_engine.get_session()
    try:
        query = session.query(Inventory)
        if low_stock_only:
            query = query.filter(Inventory.status == "Low Stock")
        items = query.order_by(Inventory.id.asc()).limit(limit).all()
        return [i.to_dict() for i in items]
    finally:
        session.close()


def get_customers_list(limit: int = 100, tier: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve customer accounts (55 records)."""
    session = db_engine.get_session()
    try:
        query = session.query(Customer)
        if tier:
            query = query.filter(Customer.tier.ilike(f"%{tier}%"))
        if status:
            query = query.filter(Customer.status == status)
        customers = query.order_by(Customer.id.asc()).limit(limit).all()
        return [c.to_dict() for c in customers]
    finally:
        session.close()


def get_master_records_list() -> List[Dict[str, Any]]:
    """Retrieve all client master records (5 records)."""
    session = db_engine.get_session()
    try:
        clients = session.query(ClientMaster).order_by(ClientMaster.id.asc()).all()
        return [c.to_dict() for c in clients]
    finally:
        session.close()


def get_orders_list(limit: int = 50, customer_code: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve order records (115 records)."""
    session = db_engine.get_session()
    try:
        query = session.query(Order)
        if customer_code:
            query = query.filter(Order.customer_code == customer_code)
        if status:
            query = query.filter(Order.status == status)
        orders = query.order_by(Order.id.desc()).limit(limit).all()
        return [o.to_dict() for o in orders]
    finally:
        session.close()


def get_order_items_list(order_number: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve order line items."""
    session = db_engine.get_session()
    try:
        query = session.query(OrderItem)
        if order_number:
            query = query.filter(OrderItem.order_number == order_number)
        items = query.all()
        return [it.to_dict() for it in items]
    finally:
        session.close()


def get_payments_list(limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieve payment records."""
    session = db_engine.get_session()
    try:
        payments = session.query(Payment).order_by(Payment.id.desc()).limit(limit).all()
        return [p.to_dict() for p in payments]
    finally:
        session.close()


def _get_entity_name_maps(session) -> tuple[Dict[str, str], Dict[str, str]]:
    """Helper to build code -> name maps for rich transaction display."""
    c_map = {}
    for c in session.query(Customer).all():
        c_map[c.customer_code] = c.company_name
    for m in session.query(ClientMaster).all():
        c_map[m.client_code] = m.company_name

    p_map = {}
    for p in session.query(Product).all():
        p_map[p.product_code] = p.name

    return c_map, p_map


def get_transactions_list(limit: int = 50, client_code: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve transaction records with client and product resolution (215 records)."""
    session = db_engine.get_session()
    try:
        c_map, p_map = _get_entity_name_maps(session)
        query = session.query(Transaction)
        if client_code:
            query = query.filter(Transaction.client_code == client_code)
        if status:
            query = query.filter(Transaction.status == status)
        txns = query.order_by(Transaction.id.asc()).limit(limit).all()
        return [t.to_dict(c_map, p_map) for t in txns]
    finally:
        session.close()


def get_policies_list(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve corporate policy records (10 records)."""
    session = db_engine.get_session()
    try:
        query = session.query(Policy)
        if category:
            query = query.filter(Policy.category.ilike(f"%{category}%"))
        policies = query.order_by(Policy.id.asc()).all()
        return [p.to_dict() for p in policies]
    finally:
        session.close()


def get_faqs_list(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve corporate FAQs (15 records)."""
    session = db_engine.get_session()
    try:
        query = session.query(FAQ)
        if category:
            query = query.filter(FAQ.category.ilike(f"%{category}%"))
        faqs = query.order_by(FAQ.id.asc()).all()
        return [f.to_dict() for f in faqs]
    finally:
        session.close()


def get_analytics_summary() -> Dict[str, Any]:
    """Retrieve high-level business analytics summary across all tables."""
    session = db_engine.get_session()
    try:
        total_products = session.query(Product).count()
        total_clients = session.query(ClientMaster).count()
        total_customers = session.query(Customer).count()
        total_orders = session.query(Order).count()
        total_txns = session.query(Transaction).count()
        total_inventory = session.query(Inventory).count()
        total_departments = session.query(Department).count()
        total_employees = session.query(Employee).count()
        total_suppliers = session.query(Supplier).count()
        total_policies = session.query(Policy).count()
        total_faqs = session.query(FAQ).count()

        txns = session.query(Transaction).all()
        total_revenue = sum(t.amount for t in txns if t.status == "Completed")
        pending_revenue = sum(t.amount for t in txns if t.status != "Completed")

        orders = session.query(Order).all()
        total_order_value = sum(o.total_amount for o in orders)

        return {
            "database_engine": db_engine.db_type,
            "total_products": total_products,
            "total_clients": total_clients,
            "total_customers": total_customers,
            "total_orders": total_orders,
            "total_order_value_usd": total_order_value,
            "total_transactions": total_txns,
            "completed_transactions": len([t for t in txns if t.status == "Completed"]),
            "pending_transactions": len([t for t in txns if t.status != "Completed"]),
            "total_revenue_usd": total_revenue,
            "pending_revenue_usd": pending_revenue,
            "total_inventory_items": total_inventory,
            "total_departments": total_departments,
            "total_employees": total_employees,
            "total_suppliers": total_suppliers,
            "total_policies": total_policies,
            "total_faqs": total_faqs,
        }
    finally:
        session.close()


def search_records(query_str: str) -> Dict[str, Any]:
    """Search across products, customers, transactions, inventory, and policies."""
    session = db_engine.get_session()
    q = f"%{query_str.lower()}%"
    try:
        c_map, p_map = _get_entity_name_maps(session)

        p_matches = session.query(Product).filter(
            (Product.name.ilike(q)) | (Product.product_code.ilike(q)) | (Product.tier.ilike(q))
        ).all()

        c_matches = session.query(Customer).filter(
            (Customer.company_name.ilike(q)) | (Customer.customer_code.ilike(q)) | (Customer.industry.ilike(q))
        ).all()

        t_matches = session.query(Transaction).filter(
            (Transaction.transaction_ref.ilike(q)) | (Transaction.client_code.ilike(q)) | (Transaction.product_code.ilike(q))
        ).all()

        inv_matches = session.query(Inventory).filter(
            (Inventory.sku.ilike(q)) | (Inventory.product_code.ilike(q)) | (Inventory.warehouse_location.ilike(q))
        ).all()

        pol_matches = session.query(Policy).filter(
            (Policy.title.ilike(q)) | (Policy.policy_code.ilike(q)) | (Policy.category.ilike(q))
        ).all()

        return {
            "products": [p.to_dict() for p in p_matches],
            "customers": [c.to_dict() for c in c_matches],
            "transactions": [t.to_dict(c_map, p_map) for t in t_matches],
            "inventory": [i.to_dict() for i in inv_matches],
            "policies": [pol.to_dict() for pol in pol_matches],
        }
    finally:
        session.close()


def query_database_smart(prompt: str) -> Optional[str]:
    """Inspect user query and return formatted markdown tables if relevant to DB."""
    p_lower = prompt.lower()

    # Keywords for DB triggers
    is_db_summary = any(k in p_lower for k in [
        "database summary", "database stats", "records in database", "how many records",
        "show database", "database status"
    ])
    is_inventory_query = any(k in p_lower for k in [
        "inventory", "warehouse", "stock level", "stock quantity", "in stock",
        "low stock", "reorder level", "sku-"
    ])
    is_order_query = any(k in p_lower for k in [
        "order list", "show orders", "latest orders", "order status", "sales orders", "ord-", "purchase order"
    ])
    is_customer_query = any(k in p_lower for k in [
        "customer accounts", "customer list", "show customers", "list customers", "cust-",
        "client accounts", "master records", "apex financial", "biogenix", "vertex logistics",
        "omniretail", "cybershield", "quantum capital", "meridian health"
    ])
    is_product_query = any(k in p_lower for k in [
        "product catalog", "show products", "list products", "pricing plans", "product pricing",
        "product tiers", "nd-ent-", "nd-cld-", "nd-sec-", "nd-api-"
    ])
    is_txn_query = any(k in p_lower for k in [
        "transaction", "transactions", "txn-", "sales revenue", "payment records"
    ])
    is_policy_db_query = any(k in p_lower for k in [
        "database policies", "company policies table", "list policies", "show policies",
        "policy list", "corporate policies table", "pol-0"
    ])
    is_dept_query = any(k in p_lower for k in [
        "department list", "company departments", "show departments", "corporate departments", "dep-"
    ])

    if not (is_db_summary or is_inventory_query or is_order_query or is_customer_query or
            is_product_query or is_txn_query or is_policy_db_query or is_dept_query):
        return None

    response_parts = []

    # 1. DB Summary
    if is_db_summary:
        stats = get_analytics_summary()
        response_parts.append(
            f"### NexaData Enterprise Relational Database Status\n"
            f"- **Database Engine**: `{stats['database_engine'].upper()}`\n"
            f"- **Products**: {stats['total_products']} catalog items\n"
            f"- **Customer Accounts**: {stats['total_customers']} enterprise accounts\n"
            f"- **Orders Processed**: {stats['total_orders']} orders (Total Value: **${stats['total_order_value_usd']:,.2f} USD**)\n"
            f"- **Transactions**: {stats['total_transactions']} ({stats['completed_transactions']} Completed, {stats['pending_transactions']} Pending)\n"
            f"- **Recognized Revenue**: **${stats['total_revenue_usd']:,.2f} USD** (Pending: ${stats['pending_revenue_usd']:,.2f})\n"
            f"- **Inventory**: {stats['total_inventory_items']} warehouse stock records\n"
            f"- **Departments & Staff**: {stats['total_departments']} departments, {stats['total_employees']} staff directory entries\n"
            f"- **Suppliers & Vendors**: {stats['total_suppliers']} infrastructure suppliers\n"
            f"- **Policies & FAQs**: {stats['total_policies']} enterprise policies, {stats['total_faqs']} knowledge base FAQs\n"
        )

    # 2. Inventory Query
    if is_inventory_query:
        low_only = "low" in p_lower
        items = get_inventory_list(limit=25, low_stock_only=low_only)
        table_rows = [
            "| SKU | Product Code | Warehouse / Cluster | Available | Reserved | Reorder Level | Status |",
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
        ]
        for it in items:
            status_badge = "[Low Stock]" if it["status"] == "Low Stock" else "[In Stock]"
            table_rows.append(
                f"| `{it['sku']}` | `{it['product_code']}` | {it['warehouse_location']} | **{it['quantity_available']}** | {it['quantity_reserved']} | {it['reorder_level']} | {status_badge} |"
            )
        response_parts.append(
            f"### NexaData Inventory & Warehouse Stock ({len(items)} Records)\n\n" +
            "\n".join(table_rows)
        )

    # 3. Orders Query
    if is_order_query:
        orders = get_orders_list(limit=15)
        table_rows = [
            "| Order # | Customer | Amount | Status | Payment | Date | Notes |",
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
        ]
        for o in orders:
            status_badge = f"[{o['status']}]"
            table_rows.append(
                f"| `{o['order_number']}` | `{o['customer_code']}` | **${o['net_amount']:,.2f}** | {status_badge} | `{o['payment_status']}` | {o['order_date']} | {o['notes'][:50]}... |"
            )
        response_parts.append(
            f"### Recent Orders & Sales Contracts ({len(orders)} Records)\n\n" +
            "\n".join(table_rows)
        )

    # 4. Customers Query
    if is_customer_query:
        customers = get_customers_list(limit=15)
        table_rows = [
            "| Customer Code | Company Name | Industry | Tier | Credit Limit | Balance | Status |",
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
        ]
        for c in customers:
            table_rows.append(
                f"| `{c['customer_code']}` | **{c['company_name']}** | {c['industry']} | {c['tier']} | ${c['credit_limit']:,.0f} | ${c['account_balance']:,.2f} | `{c['status']}` |"
            )
        response_parts.append(
            f"### Enterprise Customer Accounts ({len(customers)} of 55 Records Displayed)\n\n" +
            "\n".join(table_rows)
        )

    # 5. Products Query
    if is_product_query:
        products = get_products_list()
        table_rows = [
            "| Code | Product Name | Tier | Price | Billing | Description |",
            "| :--- | :--- | :--- | :--- | :--- | :--- |"
        ]
        for p in products[:12]:
            table_rows.append(
                f"| `{p['product_code']}` | **{p['name']}** | {p['tier']} | ${p['price']:,.2f} | {p['billing_type']} | {p['description'][:60]}... |"
            )
        response_parts.append(
            f"### Product Catalog ({len(products)} Database Records)\n\n" +
            "\n".join(table_rows)
        )

    # 6. Transactions Query
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
            status_badge = f"[{t['status']}]"
            table_rows.append(
                f"| `{t['transaction_ref']}` | **{t['client_name']}** | `{t['product_code']}` | ${t['amount']:,.2f} | {status_badge} | {t['payment_method']} | {t['transaction_date']} | {t['notes']} |"
            )

        header = f"### Enterprise Transactions ({len(txns)} of 215 Records)"
        if matched_client:
            header += f" for Client `{matched_client}`"

        response_parts.append(header + "\n\n" + "\n".join(table_rows))

    # 7. Policies DB Query
    if is_policy_db_query:
        policies = get_policies_list()
        table_rows = [
            "| Policy Code | Title | Category | Effective Date | Summary Guarantee |",
            "| :--- | :--- | :--- | :--- | :--- |"
        ]
        for pol in policies:
            table_rows.append(
                f"| `{pol['policy_code']}` | **{pol['title']}** | {pol['category']} | {pol['effective_date']} | {pol['summary']} |"
            )
        response_parts.append(
            f"### Official Corporate Policies (Database Records)\n\n" +
            "\n".join(table_rows)
        )

    # 8. Departments Query
    if is_dept_query:
        deps = get_departments_list()
        table_rows = [
            "| Code | Department Name | Head of Department | Budget | Location | Staff Count |",
            "| :--- | :--- | :--- | :--- | :--- | :--- |"
        ]
        for d in deps:
            table_rows.append(
                f"| `{d['department_code']}` | **{d['name']}** | {d['head_of_department']} | ${d['budget']:,.0f} | {d['location']} | {d['employee_count']} |"
            )
        response_parts.append(
            f"### Corporate Departments ({len(deps)} Departments)\n\n" +
            "\n".join(table_rows)
        )

    if response_parts:
        return "\n\n---\n\n".join(response_parts)
    return None


# ============================================================================
# Chat Persistence & Sync Layer
# ============================================================================

def save_chat_session(session_id: str, title: str, mode: str = "company", messages: Optional[List[Dict[str, Any]]] = None, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Save or update chat session and sync its message history."""
    import json
    session = db_engine.get_session()
    try:
        conv = session.query(ChatSession).filter(ChatSession.session_id == session_id).first()
        if not conv:
            conv = ChatSession(session_id=session_id, user_id=user_id, title=title[:190], mode=mode)
            session.add(conv)
        else:
            conv.title = title[:190]
            conv.mode = mode
            if user_id and not conv.user_id:
                conv.user_id = user_id
            conv.updated_at = datetime.now(timezone.utc)
        session.commit()

        if messages:
            session.query(ChatMessage).filter(ChatMessage.session_id == session_id).delete()
            for m in messages:
                role = m.get("role") or ("user" if m.get("type") == "user" else "assistant")
                content = m.get("content") or m.get("text") or m.get("reply") or ""
                sources = m.get("sources", [])
                src_json = json.dumps(sources) if sources else None
                ts = m.get("timestamp")
                session.add(ChatMessage(
                    session_id=session_id,
                    role=role,
                    content=content,
                    sources_json=src_json,
                    timestamp=ts
                ))
            session.commit()
        return conv.to_dict()
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to save chat session: {e}")
        return {"session_id": session_id, "title": title, "mode": mode, "user_id": user_id}
    finally:
        session.close()

def get_chat_sessions(limit: int = 30, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve recent chat sessions from database, optionally filtered by user_id."""
    session = db_engine.get_session()
    try:
        query = session.query(ChatSession)
        if user_id:
            query = query.filter(ChatSession.user_id == user_id)
        sessions = query.order_by(ChatSession.updated_at.desc()).limit(limit).all()
        result = []
        for s in sessions:
            item = s.to_dict()
            last_msg = session.query(ChatMessage).filter(ChatMessage.session_id == s.session_id).order_by(ChatMessage.id.desc()).first()
            item["last_message"] = last_msg.content[:80] if last_msg else ""
            result.append(item)
        return result
    finally:
        session.close()

def get_chat_session_messages(session_id: str) -> List[Dict[str, Any]]:
    """Retrieve all messages for a specific session."""
    session = db_engine.get_session()
    try:
        msgs = session.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.id.asc()).all()
        return [m.to_dict() for m in msgs]
    finally:
        session.close()

def delete_chat_session(session_id: str, user_id: Optional[str] = None) -> bool:
    """Delete a chat session and its messages from database, optionally verifying user_id."""
    session = db_engine.get_session()
    try:
        conv = session.query(ChatSession).filter(ChatSession.session_id == session_id).first()
        if not conv:
            return False
        if user_id and conv.user_id and conv.user_id != user_id:
            return False
        session.query(ChatMessage).filter(ChatMessage.session_id == session_id).delete()
        session.delete(conv)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to delete chat session: {e}")
        return False
    finally:
        session.close()


# ============================================================================
# User Account Helpers
# ============================================================================

def create_user(email: str, password_hash: str, full_name: str, role: str = "user", user_id: Optional[str] = None) -> Dict[str, Any]:
    """Create a new user account in database."""
    import uuid
    session = db_engine.get_session()
    try:
        uid = user_id or f"usr_{uuid.uuid4().hex[:12]}"
        user = User(
            user_id=uid,
            email=email.strip().lower(),
            password_hash=password_hash,
            full_name=full_name.strip(),
            role=role,
            is_active=True
        )
        session.add(user)
        session.commit()
        return user.to_dict()
    finally:
        session.close()

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Retrieve user by normalized email address."""
    session = db_engine.get_session()
    try:
        user = session.query(User).filter(User.email == email.strip().lower()).first()
        if not user:
            return None
        res = user.to_dict()
        res["password_hash"] = user.password_hash
        return res
    finally:
        session.close()

def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve user by user_id."""
    session = db_engine.get_session()
    try:
        user = session.query(User).filter(User.user_id == user_id).first()
        return user.to_dict() if user else None
    finally:
        session.close()

def update_user_last_login(user_id: str):
    """Update last_login_at timestamp for a user."""
    session = db_engine.get_session()
    try:
        user = session.query(User).filter(User.user_id == user_id).first()
        if user:
            user.last_login_at = datetime.now(timezone.utc)
            session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to update user last login: {e}")
    finally:
        session.close()


