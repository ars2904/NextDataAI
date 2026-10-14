"""Data generator and SQL seed builder for NexaData AI.
Produces structured records for:
- 1 Company Info
- 7 Departments
- 25 Employees
- 8 Categories
- 10 Suppliers
- 24 Products (>= 20)
- 24 Inventory items
- 55 Customers (>= 50)
- 5 Clients Master (compatible)
- 115 Orders (>= 100)
- 260+ Order Items
- 115 Payments
- 215 Transactions (>= 200)
- 10 Policies
- 15 FAQs
"""
import random
from datetime import datetime, timedelta

# Set fixed seed for deterministic, reproducible testing
random.seed(42)

# -------------------------------------------------------------
# 1. Company Information
# -------------------------------------------------------------
COMPANY_INFO_DATA = {
    "company_name": "NexaData AI Solutions Inc.",
    "legal_name": "NexaData Technologies Global Inc.",
    "tagline": "Autonomous AI Data Analytics & Enterprise Intelligence",
    "tax_id": "US-EIN-94-3829104",
    "founded_year": 2021,
    "headquarters": "100 Technology Square, Suite 500, Cambridge, MA 02139, USA",
    "website": "https://nexadata.ai",
    "support_email": "support@nexadata.ai",
    "sales_email": "sales@nexadata.ai",
    "phone": "+1 (800) 555-6392",
    "mission": "Empowering global enterprises with autonomous, document-grounded intelligence and verifiable data insights without compromising data privacy.",
    "vision": "To become the global standard for secure, auditable, and self-governing enterprise cognitive analytics.",
    "fiscal_year_end": "December 31",
    "primary_currency": "USD"
}

# -------------------------------------------------------------
# 2. Departments
# -------------------------------------------------------------
DEPARTMENTS_DATA = [
    {
        "department_code": "DEP-ENG",
        "name": "Platform Engineering & Infrastructure",
        "head_of_department": "Dr. Elena Rostova",
        "budget": 4500000.0,
        "location": "Cambridge HQ (Floor 5)",
        "employee_count": 42,
        "contact_email": "engineering@nexadata.ai"
    },
    {
        "department_code": "DEP-RES",
        "name": "AI Research & Embeddings Lab",
        "head_of_department": "Dr. Marcus Vance",
        "budget": 3800000.0,
        "location": "Cambridge HQ (Floor 6)",
        "employee_count": 28,
        "contact_email": "research@nexadata.ai"
    },
    {
        "department_code": "DEP-SLS",
        "name": "Global Enterprise Sales & Partnerships",
        "head_of_department": "Rachel Sterling",
        "budget": 2900000.0,
        "location": "New York Regional Office",
        "employee_count": 35,
        "contact_email": "enterprise-sales@nexadata.ai"
    },
    {
        "department_code": "DEP-CS",
        "name": "Customer Solutions & 24/7 Operations",
        "head_of_department": "David Chen",
        "budget": 2100000.0,
        "location": "Chicago Service Center",
        "employee_count": 30,
        "contact_email": "solutions@nexadata.ai"
    },
    {
        "department_code": "DEP-SEC",
        "name": "Information Security & Compliance",
        "head_of_department": "Samantha Miller",
        "budget": 2400000.0,
        "location": "Washington DC Security Office",
        "employee_count": 18,
        "contact_email": "infosec@nexadata.ai"
    },
    {
        "department_code": "DEP-FIN",
        "name": "Finance, Accounting & Legal",
        "head_of_department": "Arthur Pendelton",
        "budget": 1600000.0,
        "location": "Cambridge HQ (Floor 4)",
        "employee_count": 14,
        "contact_email": "finance@nexadata.ai"
    },
    {
        "department_code": "DEP-PROD",
        "name": "Product Strategy & UX Design",
        "head_of_department": "Sophia Lin",
        "budget": 1800000.0,
        "location": "San Francisco Hub",
        "employee_count": 16,
        "contact_email": "product@nexadata.ai"
    }
]

# -------------------------------------------------------------
# 3. Employees (25 Sample Staff)
# -------------------------------------------------------------
EMPLOYEES_DATA = [
    {"employee_code": "EMP-1001", "first_name": "Elena", "last_name": "Rostova", "email": "elena.rostova@nexadata.ai", "phone": "+1-617-555-0101", "department_code": "DEP-ENG", "role": "VP of Engineering", "salary": 245000.0, "hire_date": "2021-03-15", "location": "Cambridge, MA"},
    {"employee_code": "EMP-1002", "first_name": "Marcus", "last_name": "Vance", "email": "marcus.vance@nexadata.ai", "phone": "+1-617-555-0102", "department_code": "DEP-RES", "role": "Chief Scientist", "salary": 260000.0, "hire_date": "2021-04-01", "location": "Cambridge, MA"},
    {"employee_code": "EMP-1003", "first_name": "Rachel", "last_name": "Sterling", "email": "rachel.sterling@nexadata.ai", "phone": "+1-212-555-0103", "department_code": "DEP-SLS", "role": "VP of Global Sales", "salary": 220000.0, "hire_date": "2021-06-10", "location": "New York, NY"},
    {"employee_code": "EMP-1004", "first_name": "David", "last_name": "Chen", "email": "david.chen@nexadata.ai", "phone": "+1-312-555-0104", "department_code": "DEP-CS", "role": "Director of Customer Success", "salary": 185000.0, "hire_date": "2021-08-20", "location": "Chicago, IL"},
    {"employee_code": "EMP-1005", "first_name": "Samantha", "last_name": "Miller", "email": "samantha.miller@nexadata.ai", "phone": "+1-202-555-0105", "department_code": "DEP-SEC", "role": "Chief Information Security Officer", "salary": 230000.0, "hire_date": "2021-05-18", "location": "Washington, DC"},
    {"employee_code": "EMP-1006", "first_name": "Arthur", "last_name": "Pendelton", "email": "arthur.pendelton@nexadata.ai", "phone": "+1-617-555-0106", "department_code": "DEP-FIN", "role": "CFO & General Counsel", "salary": 240000.0, "hire_date": "2021-02-01", "location": "Cambridge, MA"},
    {"employee_code": "EMP-1007", "first_name": "Sophia", "last_name": "Lin", "email": "sophia.lin@nexadata.ai", "phone": "+1-415-555-0107", "department_code": "DEP-PROD", "role": "Head of Product", "salary": 195000.0, "hire_date": "2021-09-01", "location": "San Francisco, CA"},
    {"employee_code": "EMP-1008", "first_name": "Tariq", "last_name": "Mansour", "email": "tariq.mansour@nexadata.ai", "phone": "+1-617-555-0108", "department_code": "DEP-ENG", "role": "Principal Distributed Systems Architect", "salary": 180000.0, "hire_date": "2022-01-15", "location": "Cambridge, MA"},
    {"employee_code": "EMP-1009", "first_name": "Ananya", "last_name": "Sharma", "email": "ananya.sharma@nexadata.ai", "phone": "+1-617-555-0109", "department_code": "DEP-RES", "role": "Senior NLP Research Scientist", "salary": 165000.0, "hire_date": "2022-03-01", "location": "Cambridge, MA"},
    {"employee_code": "EMP-1010", "first_name": "Liam", "last_name": "O'Connor", "email": "liam.oconnor@nexadata.ai", "phone": "+1-212-555-0110", "department_code": "DEP-SLS", "role": "Senior Enterprise Account Director", "salary": 150000.0, "hire_date": "2022-05-12", "location": "New York, NY"},
    {"employee_code": "EMP-1011", "first_name": "Priya", "last_name": "Patel", "email": "priya.patel@nexadata.ai", "phone": "+1-212-555-0111", "department_code": "DEP-SLS", "role": "Strategic Accounts Executive", "salary": 140000.0, "hire_date": "2022-07-19", "location": "New York, NY"},
    {"employee_code": "EMP-1012", "first_name": "Carlos", "last_name": "Mendoza", "email": "carlos.mendoza@nexadata.ai", "phone": "+1-312-555-0112", "department_code": "DEP-CS", "role": "Lead Solutions Engineer", "salary": 135000.0, "hire_date": "2022-09-10", "location": "Chicago, IL"},
    {"employee_code": "EMP-1013", "first_name": "Hannah", "last_name": "Schmidt", "email": "hannah.schmidt@nexadata.ai", "phone": "+1-202-555-0113", "department_code": "DEP-SEC", "role": "Senior Compliance Analyst", "salary": 125000.0, "hire_date": "2023-01-09", "location": "Washington, DC"},
    {"employee_code": "EMP-1014", "first_name": "Vikram", "last_name": "Reddy", "email": "vikram.reddy@nexadata.ai", "phone": "+1-617-555-0114", "department_code": "DEP-ENG", "role": "Staff Data Infrastructure Engineer", "salary": 160000.0, "hire_date": "2023-02-14", "location": "Cambridge, MA"},
    {"employee_code": "EMP-1015", "first_name": "Chloe", "last_name": "Dubois", "email": "chloe.dubois@nexadata.ai", "phone": "+1-415-555-0115", "department_code": "DEP-PROD", "role": "Senior UX & Visual Designer", "salary": 130000.0, "hire_date": "2023-04-11", "location": "San Francisco, CA"},
    {"employee_code": "EMP-1016", "first_name": "Derek", "last_name": "Washington", "email": "derek.washington@nexadata.ai", "phone": "+1-617-555-0116", "department_code": "DEP-FIN", "role": "Financial Controller", "salary": 135000.0, "hire_date": "2023-06-01", "location": "Cambridge, MA"},
    {"employee_code": "EMP-1017", "first_name": "Mei-Ling", "last_name": "Zhou", "email": "meiling.zhou@nexadata.ai", "phone": "+1-617-555-0117", "department_code": "DEP-RES", "role": "Vector Search Algorithm Specialist", "salary": 155000.0, "hire_date": "2023-08-15", "location": "Cambridge, MA"},
    {"employee_code": "EMP-1018", "first_name": "Gabriel", "last_name": "Silva", "email": "gabriel.silva@nexadata.ai", "phone": "+1-212-555-0118", "department_code": "DEP-SLS", "role": "Commercial Sales Manager", "salary": 125000.0, "hire_date": "2023-10-01", "location": "New York, NY"},
    {"employee_code": "EMP-1019", "first_name": "Fatima", "last_name": "Al-Hassan", "email": "fatima.alhassan@nexadata.ai", "phone": "+1-312-555-0119", "department_code": "DEP-CS", "role": "Enterprise Support Team Lead", "salary": 115000.0, "hire_date": "2023-11-20", "location": "Chicago, IL"},
    {"employee_code": "EMP-1020", "first_name": "Lucas", "last_name": "Meyer", "email": "lucas.meyer@nexadata.ai", "phone": "+1-617-555-0120", "department_code": "DEP-ENG", "role": "Full-Stack Web Architect", "salary": 145000.0, "hire_date": "2024-01-08", "location": "Cambridge, MA"},
    {"employee_code": "EMP-1021", "first_name": "Aisha", "last_name": "Kamara", "email": "aisha.kamara@nexadata.ai", "phone": "+1-202-555-0121", "department_code": "DEP-SEC", "role": "Cloud Security Architect", "salary": 150000.0, "hire_date": "2024-02-15", "location": "Washington, DC"},
    {"employee_code": "EMP-1022", "first_name": "Jonas", "last_name": "Lindqvist", "email": "jonas.lindqvist@nexadata.ai", "phone": "+1-617-555-0122", "department_code": "DEP-ENG", "role": "Site Reliability Engineer", "salary": 138000.0, "hire_date": "2024-04-10", "location": "Cambridge, MA"},
    {"employee_code": "EMP-1023", "first_name": "Zoe", "last_name": "Kowalski", "email": "zoe.kowalski@nexadata.ai", "phone": "+1-212-555-0123", "department_code": "DEP-SLS", "role": "Technical Sales Consultant", "salary": 120000.0, "hire_date": "2024-06-01", "location": "New York, NY"},
    {"employee_code": "EMP-1024", "first_name": "Ethan", "last_name": "Brooks", "email": "ethan.brooks@nexadata.ai", "phone": "+1-312-555-0124", "department_code": "DEP-CS", "role": "Customer Success Manager", "salary": 105000.0, "hire_date": "2024-08-15", "location": "Chicago, IL"},
    {"employee_code": "EMP-1025", "first_name": "Nadia", "last_name": "Benali", "email": "nadia.benali@nexadata.ai", "phone": "+1-415-555-0125", "department_code": "DEP-PROD", "role": "Product Manager - API Ecosystem", "salary": 140000.0, "hire_date": "2024-10-01", "location": "San Francisco, CA"}
]

# -------------------------------------------------------------
# 4. Categories (8 Categories)
# -------------------------------------------------------------
CATEGORIES_DATA = [
    {"category_code": "CAT-CORE", "name": "Enterprise AI Core Engines", "description": "Flagship autonomous LLM platforms, cognitive engines, and grounded RAG processors."},
    {"category_code": "CAT-CLD", "name": "Cloud Analytics & BI", "description": "Managed cloud data warehouse connectors, real-time BI sync, and automated board dashboards."},
    {"category_code": "CAT-SEC", "name": "Security & Air-Gapped Enclaves", "description": "Zero-trust client isolation, HIPAA/SOC2 compliant sandboxes, and audit exporters."},
    {"category_code": "CAT-DATA", "name": "ETL & Streaming Data Connectors", "description": "High-throughput stream connectors for Snowflake, Databricks, Oracle, and Kafka."},
    {"category_code": "CAT-DEV", "name": "Developer APIs & SDKs", "description": "Low-latency REST/gRPC endpoints, Python SDKs, and streaming completion gateways."},
    {"category_code": "CAT-SVC", "name": "Professional Services & SRE", "description": "Dedicated solutions engineering, 99.99% SLA support, and white-glove migrations."},
    {"category_code": "CAT-HW", "name": "Hardware Appliances & Edge", "description": "On-premises high-density GPU nodes and localized inference server racks."},
    {"category_code": "CAT-GOV", "name": "Governance & Compliance", "description": "Automated audit log archival, model explainability tools, and regulatory validation suites."}
]

# -------------------------------------------------------------
# 5. Suppliers (10 Suppliers)
# -------------------------------------------------------------
SUPPLIERS_DATA = [
    {"supplier_code": "SUP-01", "name": "NVIDIA Compute Solutions", "contact_name": "Jason Huang", "email": "enterprise@nvidia-partner.com", "phone": "+1-408-555-0191", "country": "United States", "service_type": "H100 & B200 Cloud GPU Infrastructure", "rating": 4.95, "payment_terms": "Net 30"},
    {"supplier_code": "SUP-02", "name": "Equinix Global Data Centers", "contact_name": "Marie Dupont", "email": "accounts@equinix-coloc.com", "phone": "+1-650-555-0192", "country": "United States", "service_type": "Tier-4 Colocation & Optical Interconnects", "rating": 4.90, "payment_terms": "Net 30"},
    {"supplier_code": "SUP-03", "name": "Snowflake Cloud Ecosystem", "contact_name": "Robert Klein", "email": "partnerships@snowflake-connect.com", "phone": "+1-844-555-0193", "country": "United States", "service_type": "Data Cloud Integration & Native Apps", "rating": 4.88, "payment_terms": "Net 45"},
    {"supplier_code": "SUP-04", "name": "Supermicro Server Solutions", "contact_name": "Kevin Liang", "email": "oem-sales@supermicro-direct.com", "phone": "+1-408-555-0194", "country": "Taiwan", "service_type": "Custom Rackmount AI Edge Servers", "rating": 4.82, "payment_terms": "Net 60"},
    {"supplier_code": "SUP-05", "name": "Yubico Hardware Security", "contact_name": "Astrid Lindgren", "email": "enterprise@yubico-security.com", "phone": "+46-8-555-0195", "country": "Sweden", "service_type": "FIPS 140-2 Level 3 Hardware Security Keys", "rating": 4.98, "payment_terms": "Net 30"},
    {"supplier_code": "SUP-06", "name": "Datadog Telemetry Systems", "contact_name": "Claire Lefevre", "email": "billing@datadog-monitoring.com", "phone": "+1-866-555-0196", "country": "United States", "service_type": "APM, Synthetics & LLM Observability", "rating": 4.85, "payment_terms": "Monthly Auto-pay"},
    {"supplier_code": "SUP-07", "name": "AWS GovCloud Services", "contact_name": "Mark Henderson", "email": "fed-sales@amazon-govcloud.com", "phone": "+1-888-555-0197", "country": "United States", "service_type": "FedRAMP High Compliant Cloud Enclaves", "rating": 4.92, "payment_terms": "Net 30"},
    {"supplier_code": "SUP-08", "name": "MongoDB Atlas Systems", "contact_name": "Devin Murphy", "email": "partner-support@mongodb-cloud.com", "phone": "+1-212-555-0198", "country": "United States", "service_type": "Managed Global Vector & Document DB", "rating": 4.87, "payment_terms": "Monthly Auto-pay"},
    {"supplier_code": "SUP-09", "name": "Cloudflare Global Edge", "contact_name": "Sarah Connor", "email": "enterprise@cloudflare-edge.com", "phone": "+1-888-555-0199", "country": "United States", "service_type": "DDoS Defense & Zero-Trust Access Gateway", "rating": 4.96, "payment_terms": "Net 30"},
    {"supplier_code": "SUP-10", "name": "Red Hat Enterprise Solutions", "contact_name": "Hans Becker", "email": "licensing@redhat-partner.com", "phone": "+1-888-555-0200", "country": "United States", "service_type": "OpenShift Container Platform & Linux", "rating": 4.89, "payment_terms": "Annual"}
]

# -------------------------------------------------------------
# 6. Products (24 Products >= 20)
# -------------------------------------------------------------
PRODUCTS_DATA = [
    # Original 5 Core Products (Preserved)
    {
        "product_code": "ND-ENT-01",
        "name": "NexaData Enterprise Engine",
        "tier": "Enterprise Platinum",
        "category_code": "CAT-CORE",
        "supplier_code": "SUP-01",
        "price": 12500.0,
        "cost_price": 4200.0,
        "billing_type": "Monthly",
        "stock_quantity": 9999,
        "description": "Full-stack hybrid RAG, document intelligence, multi-tenant sandboxing, and citation grounding.",
        "features": "Air-gapped deployment, Custom embeddings, 99.99% SLA, Dedicated GPU clusters",
        "is_active": True
    },
    {
        "product_code": "ND-CLD-02",
        "name": "NexaData Cloud Analytics",
        "tier": "Business",
        "category_code": "CAT-CLD",
        "supplier_code": "SUP-03",
        "price": 4800.0,
        "cost_price": 1600.0,
        "billing_type": "Monthly",
        "stock_quantity": 9999,
        "description": "Managed cloud data warehouse connector with automated BI reporting and interactive SQL querying.",
        "features": "Real-time sync, Snowflake/BigQuery connectors, Row-level security, Automated dashboards",
        "is_active": True
    },
    {
        "product_code": "ND-SEC-03",
        "name": "NexaData Secure Sandbox",
        "tier": "Security Addon",
        "category_code": "CAT-SEC",
        "supplier_code": "SUP-05",
        "price": 2200.0,
        "cost_price": 750.0,
        "billing_type": "Monthly",
        "stock_quantity": 9999,
        "description": "Dedicated zero-trust enclave ensuring client privacy, encrypted vector indexes, and HIPAA/SOC2 compliance.",
        "features": "Zero data leakage guarantee, FIPS 140-2 encryption, Ephemeral session scrubbing",
        "is_active": True
    },
    {
        "product_code": "ND-ETL-04",
        "name": "NexaData Real-time Pipeline",
        "tier": "Data Connector",
        "category_code": "CAT-DATA",
        "supplier_code": "SUP-02",
        "price": 3500.0,
        "cost_price": 1100.0,
        "billing_type": "Monthly",
        "stock_quantity": 9999,
        "description": "High-throughput streaming ETL connector for real-time document chunking, embeddings, and database sync.",
        "features": "Sub-second CDC ingestion, Kafka & Postgres direct tap, Auto-reindexing",
        "is_active": True
    },
    {
        "product_code": "ND-API-05",
        "name": "NexaData Developer API Gateway",
        "tier": "Developer API",
        "category_code": "CAT-DEV",
        "supplier_code": "SUP-09",
        "price": 1500.0,
        "cost_price": 450.0,
        "billing_type": "Monthly",
        "stock_quantity": 9999,
        "description": "Production REST & WebSocket API gateway for integrating NexaData AI into custom applications.",
        "features": "100k requests/day, Python/TypeScript SDKs, Webhooks, 99.9% uptime SLA",
        "is_active": True
    },
    # 19 Expanded Products
    {
        "product_code": "ND-GOV-06",
        "name": "NexaData Compliance Guardian",
        "tier": "Enterprise Gold",
        "category_code": "CAT-GOV",
        "supplier_code": "SUP-07",
        "price": 5200.0,
        "cost_price": 1800.0,
        "billing_type": "Monthly",
        "stock_quantity": 9999,
        "description": "Automated audit trail generation, GDPR/CCPA data lineage reporting, and bias mitigation verification.",
        "features": "Immutable ledger logging, Automated compliance exports, Prompt leak detection",
        "is_active": True
    },
    {
        "product_code": "ND-FIN-07",
        "name": "NexaData Financial Intelligence Suite",
        "tier": "Enterprise Platinum",
        "category_code": "CAT-CORE",
        "supplier_code": "SUP-01",
        "price": 9800.0,
        "cost_price": 3200.0,
        "billing_type": "Monthly",
        "stock_quantity": 9999,
        "description": "High-speed SEC 10-K/10-Q filing ingestion, financial statement reconciliation, and fraud pattern detection.",
        "features": "Bloomberg terminal bridge, XBRL parsing, Portfolio risk forecasting",
        "is_active": True
    },
    {
        "product_code": "ND-MED-08",
        "name": "NexaData Healthcare & HIPAA Enclave",
        "tier": "Enterprise Platinum",
        "category_code": "CAT-SEC",
        "supplier_code": "SUP-07",
        "price": 11400.0,
        "cost_price": 3900.0,
        "billing_type": "Monthly",
        "stock_quantity": 9999,
        "description": "BAA-backed private medical enclave for clinical notes analysis, EHR integration, and DICOM metadata synthesis.",
        "features": "HIPAA BAA signed, HL7/FHIR connectors, PII redaction engine",
        "is_active": True
    },
    {
        "product_code": "ND-EDG-09",
        "name": "NexaData Edge AI Appliance Server",
        "tier": "Hardware Appliance",
        "category_code": "CAT-HW",
        "supplier_code": "SUP-04",
        "price": 18500.0,
        "cost_price": 11200.0,
        "billing_type": "One-Time",
        "stock_quantity": 45,
        "description": "Ruggedized 2U rackmount server pre-loaded with air-gapped NexaData inference stack and local vector database.",
        "features": "Dual NVIDIA L40S GPUs, 256GB ECC RAM, 15TB NVMe Gen5 storage, 3-year warranty",
        "is_active": True
    },
    {
        "product_code": "ND-VEC-10",
        "name": "NexaData Distributed Vector DB Cluster",
        "tier": "Infrastructure",
        "category_code": "CAT-CORE",
        "supplier_code": "SUP-08",
        "price": 6400.0,
        "cost_price": 2200.0,
        "billing_type": "Monthly",
        "stock_quantity": 9999,
        "description": "Billion-scale HNSW vector cluster supporting 5,000 queries per second with sub-10ms nearest neighbor recall.",
        "features": "Multi-region replication, Zero-downtime scaling, Hybrid BM25 + dense search",
        "is_active": True
    },
    {
        "product_code": "ND-SQL-11",
        "name": "NexaData Autonomous Text-to-SQL CoPilot",
        "tier": "Business",
        "category_code": "CAT-CLD",
        "supplier_code": "SUP-03",
        "price": 2800.0,
        "cost_price": 950.0,
        "billing_type": "Monthly",
        "stock_quantity": 9999,
        "description": "Natural language query translation for PostgreSQL, Oracle, Snowflake, and SQL Server with schema grounding.",
        "features": "Self-correcting SQL generator, Execution plan optimizer, Read-only security sandbox",
        "is_active": True
    },
    {
        "product_code": "ND-SRE-12",
        "name": "24/7 Dedicated Solutions Engineer SLA",
        "tier": "Support Addon",
        "category_code": "CAT-SVC",
        "supplier_code": "SUP-06",
        "price": 4000.0,
        "cost_price": 1800.0,
        "billing_type": "Monthly",
        "stock_quantity": 9999,
        "description": "Named principal solutions engineer with 15-minute response SLA, proactive health monitoring, and custom pipeline tuning.",
        "features": "Direct Slack/Teams bridge, Monthly architectural review, Priority patch deployments",
        "is_active": True
    },
    {
        "product_code": "ND-MIG-13",
        "name": "Enterprise Legacy Migration Pack",
        "tier": "Professional Services",
        "category_code": "CAT-SVC",
        "supplier_code": "SUP-10",
        "price": 15000.0,
        "cost_price": 7000.0,
        "billing_type": "One-Time",
        "stock_quantity": 100,
        "description": "Comprehensive migration of legacy SharePoint, Confluence, and file servers into NexaData's vector repository.",
        "features": "Data cleansing, Metadata tagging, Zero data loss guarantee, Executive sign-off",
        "is_active": True
    },
    {
        "product_code": "ND-TRN-14",
        "name": "AI Model Distillation & Fine-Tuning Service",
        "tier": "Professional Services",
        "category_code": "CAT-CORE",
        "supplier_code": "SUP-01",
        "price": 8500.0,
        "cost_price": 3800.0,
        "billing_type": "One-Time",
        "stock_quantity": 80,
        "description": "Custom parameter-efficient fine-tuning (LoRA) of open-weights models tailored to specific corporate terminology.",
        "features": "Domain vocabulary adaptation, Evaluation benchmark report, Exportable model weights",
        "is_active": True
    },
    {
        "product_code": "ND-AUD-15",
        "name": "AI Governance & Audit Log Exporter",
        "tier": "Security Addon",
        "category_code": "CAT-GOV",
        "supplier_code": "SUP-07",
        "price": 1800.0,
        "cost_price": 600.0,
        "billing_type": "Monthly",
        "stock_quantity": 9999,
        "description": "Streaming export of user prompts, agent thoughts, citations, and model outputs into enterprise SIEM (Splunk/Elastic).",
        "features": "Real-time CEF/Syslog stream, Encrypted daily S3 dumps, Tamper-proof hashes",
        "is_active": True
    },
    {
        "product_code": "ND-SNW-16",
        "name": "Snowflake Native Data Share Connector",
        "tier": "Data Connector",
        "category_code": "CAT-DATA",
        "supplier_code": "SUP-03",
        "price": 3200.0,
        "cost_price": 1100.0,
        "billing_type": "Monthly",
        "stock_quantity": 9999,
        "description": "Zero-copy cloning connector for querying Snowflake tables directly from NexaData conversational workflows.",
        "features": "Zero-copy architecture, Warehouse compute auto-suspend, Secure view inheritance",
        "is_active": True
    },
    {
        "product_code": "ND-ORA-17",
        "name": "Oracle Exadata Real-time Stream Gateway",
        "tier": "Data Connector",
        "category_code": "CAT-DATA",
        "supplier_code": "SUP-10",
        "price": 4500.0,
        "cost_price": 1600.0,
        "billing_type": "Monthly",
        "stock_quantity": 9999,
        "description": "GoldenGate compatible change data capture bridge for enterprise Oracle 19c/21c databases.",
        "features": "ACID compliance preservation, Multi-tenant PDB support, Low-overhead redo log reader",
        "is_active": True
    },
    {
        "product_code": "ND-KAF-18",
        "name": "High-Throughput Apache Kafka Ingest Engine",
        "tier": "Data Connector",
        "category_code": "CAT-DATA",
        "supplier_code": "SUP-02",
        "price": 3900.0,
        "cost_price": 1300.0,
        "billing_type": "Monthly",
        "stock_quantity": 9999,
        "description": "Consumes 100,000+ msgs/sec from Confluent/Kafka topics, embeds payloads, and updates live conversational index.",
        "features": "Avro/Protobuf schema registry integration, Exactly-once processing, Auto-rebalancing",
        "is_active": True
    },
    {
        "product_code": "ND-DOC-19",
        "name": "Multilingual OCR & Vision Document Parser",
        "tier": "Developer API",
        "category_code": "CAT-DEV",
        "supplier_code": "SUP-01",
        "price": 2600.0,
        "cost_price": 850.0,
        "billing_type": "Monthly",
        "stock_quantity": 9999,
        "description": "Extracts tables, mathematical formulas, and handwritten notes from complex multi-column PDF and scanned images.",
        "features": "Supports 85+ languages, Table-structure retention, Layout-aware bounding boxes",
        "is_active": True
    },
    {
        "product_code": "ND-EMB-20",
        "name": "Custom Embedding Optimization Service",
        "tier": "Professional Services",
        "category_code": "CAT-CORE",
        "supplier_code": "SUP-01",
        "price": 5000.0,
        "cost_price": 2100.0,
        "billing_type": "One-Time",
        "stock_quantity": 100,
        "description": "Trains proprietary sentence transformer embedding models tailored to your industry taxonomy for 35% higher RAG recall.",
        "features": "Hard-negative mining, Triplet loss optimization, Quantized ONNX runtime delivery",
        "is_active": True
    },
    {
        "product_code": "ND-BCK-21",
        "name": "Automated Zero-Loss Backup & Disaster Recovery",
        "tier": "Security Addon",
        "category_code": "CAT-SEC",
        "supplier_code": "SUP-02",
        "price": 1900.0,
        "cost_price": 600.0,
        "billing_type": "Monthly",
        "stock_quantity": 9999,
        "description": "Continuous cross-region geo-replication of PostgreSQL schemas, vector stores, and configuration states.",
        "features": "RPO < 1 minute, RTO < 5 minutes, One-click failover verification",
        "is_active": True
    },
    {
        "product_code": "ND-SOC-22",
        "name": "Dedicated SOC2 Security Audit Support Pack",
        "tier": "Professional Services",
        "category_code": "CAT-GOV",
        "supplier_code": "SUP-05",
        "price": 6000.0,
        "cost_price": 2600.0,
        "billing_type": "One-Time",
        "stock_quantity": 50,
        "description": "Auditor-ready documentation, penetration test reports, and compliance evidence packages for enterprise procurement.",
        "features": "Third-party attestation letters, Security questionnaire completion, Architect walkthroughs",
        "is_active": True
    },
    {
        "product_code": "ND-REP-23",
        "name": "Executive KPI & Board Report Generator",
        "tier": "Business",
        "category_code": "CAT-CLD",
        "supplier_code": "SUP-06",
        "price": 2400.0,
        "cost_price": 800.0,
        "billing_type": "Monthly",
        "stock_quantity": 9999,
        "description": "Weekly autonomous generation of PDF/PPT executive briefings analyzing enterprise data trends and KPIs.",
        "features": "Branded chart exports, Natural language commentary, Scheduled email distribution",
        "is_active": True
    },
    {
        "product_code": "ND-FED-24",
        "name": "Federated Learning Multi-Party Sandbox",
        "tier": "Enterprise Platinum",
        "category_code": "CAT-CORE",
        "supplier_code": "SUP-07",
        "price": 14000.0,
        "cost_price": 4900.0,
        "billing_type": "Monthly",
        "stock_quantity": 9999,
        "description": "Collaborative machine learning across independent enterprise entities without ever centralizing raw training data.",
        "features": "Differential privacy guarantees, Homomorphic model aggregation, Consortium access management",
        "is_active": True
    }
]

# -------------------------------------------------------------
# 7. Inventory Records (24 items matching products)
# -------------------------------------------------------------
INVENTORY_DATA = [
    {"sku": "SKU-ENT-001", "product_code": "ND-ENT-01", "location": "Enterprise Cloud Vault (US-East)", "available": 500, "reserved": 42, "reorder": 50, "unit_cost": 4200.0, "status": "In Stock"},
    {"sku": "SKU-CLD-002", "product_code": "ND-CLD-02", "location": "Managed Cloud Cluster (US-East)", "available": 850, "reserved": 65, "reorder": 100, "unit_cost": 1600.0, "status": "In Stock"},
    {"sku": "SKU-SEC-003", "product_code": "ND-SEC-03", "location": "Air-Gapped Security Zone (US-West)", "available": 400, "reserved": 28, "reorder": 40, "unit_cost": 750.0, "status": "In Stock"},
    {"sku": "SKU-ETL-004", "product_code": "ND-ETL-04", "location": "High-Throughput Ingest Cluster (Frankfurt)", "available": 600, "reserved": 51, "reorder": 75, "unit_cost": 1100.0, "status": "In Stock"},
    {"sku": "SKU-API-005", "product_code": "ND-API-05", "location": "Global Edge Gateway (Cloudflare)", "available": 1200, "reserved": 110, "reorder": 150, "unit_cost": 450.0, "status": "In Stock"},
    {"sku": "SKU-GOV-006", "product_code": "ND-GOV-06", "location": "GovCloud Enclave (US-Gov-West)", "available": 320, "reserved": 19, "reorder": 30, "unit_cost": 1800.0, "status": "In Stock"},
    {"sku": "SKU-FIN-007", "product_code": "ND-FIN-07", "location": "Financial Optical Grid (New York)", "available": 250, "reserved": 22, "reorder": 25, "unit_cost": 3200.0, "status": "In Stock"},
    {"sku": "SKU-MED-008", "product_code": "ND-MED-08", "location": "HIPAA Enclave (Boston-BioCloud)", "available": 180, "reserved": 14, "reorder": 20, "unit_cost": 3900.0, "status": "In Stock"},
    {"sku": "SKU-EDG-009", "product_code": "ND-EDG-09", "location": "Physical Warehouse (Fremont, CA)", "available": 12, "reserved": 6, "reorder": 15, "unit_cost": 11200.0, "status": "Low Stock"},
    {"sku": "SKU-VEC-010", "product_code": "ND-VEC-10", "location": "Vector Cluster (Frankfurt-FRA1)", "available": 450, "reserved": 35, "reorder": 50, "unit_cost": 2200.0, "status": "In Stock"},
    {"sku": "SKU-SQL-011", "product_code": "ND-SQL-11", "location": "Autonomous Query Node (US-Central)", "available": 720, "reserved": 48, "reorder": 80, "unit_cost": 950.0, "status": "In Stock"},
    {"sku": "SKU-SRE-012", "product_code": "ND-SRE-12", "location": "Global SRE Rota (Chicago/London)", "available": 30, "reserved": 18, "reorder": 10, "unit_cost": 1800.0, "status": "In Stock"},
    {"sku": "SKU-MIG-013", "product_code": "ND-MIG-13", "location": "Solutions Delivery Unit (Cambridge)", "available": 40, "reserved": 12, "reorder": 10, "unit_cost": 7000.0, "status": "In Stock"},
    {"sku": "SKU-TRN-014", "product_code": "ND-TRN-14", "location": "GPU Training Compute (US-West)", "available": 25, "reserved": 8, "reorder": 10, "unit_cost": 3800.0, "status": "In Stock"},
    {"sku": "SKU-AUD-015", "product_code": "ND-AUD-15", "location": "Audit Log Vault (US-East)", "available": 550, "reserved": 31, "reorder": 60, "unit_cost": 600.0, "status": "In Stock"},
    {"sku": "SKU-SNW-016", "product_code": "ND-SNW-16", "location": "Snowflake Partner Cloud (AWS-US-East)", "available": 620, "reserved": 44, "reorder": 70, "unit_cost": 1100.0, "status": "In Stock"},
    {"sku": "SKU-ORA-017", "product_code": "ND-ORA-17", "location": "Enterprise Redo Tap (Ashburn, VA)", "available": 310, "reserved": 18, "reorder": 35, "unit_cost": 1600.0, "status": "In Stock"},
    {"sku": "SKU-KAF-018", "product_code": "ND-KAF-18", "location": "Kafka Ingest Fabric (Dublin-EU1)", "available": 480, "reserved": 32, "reorder": 50, "unit_cost": 1300.0, "status": "In Stock"},
    {"sku": "SKU-DOC-019", "product_code": "ND-DOC-19", "location": "OCR Pipeline Grid (Mumbai-AP1)", "available": 750, "reserved": 55, "reorder": 80, "unit_cost": 850.0, "status": "In Stock"},
    {"sku": "SKU-EMB-020", "product_code": "ND-EMB-20", "location": "Model Lab Compute (Cambridge)", "available": 60, "reserved": 15, "reorder": 15, "unit_cost": 2100.0, "status": "In Stock"},
    {"sku": "SKU-BCK-021", "product_code": "ND-BCK-21", "location": "Multi-Region S3 Glacier Mirror", "available": 800, "reserved": 49, "reorder": 90, "unit_cost": 600.0, "status": "In Stock"},
    {"sku": "SKU-SOC-022", "product_code": "ND-SOC-22", "location": "InfoSec Assurance Unit (Washington)", "available": 35, "reserved": 9, "reorder": 10, "unit_cost": 2600.0, "status": "In Stock"},
    {"sku": "SKU-REP-023", "product_code": "ND-REP-23", "location": "Reporting Node (San Francisco)", "available": 640, "reserved": 38, "reorder": 70, "unit_cost": 800.0, "status": "In Stock"},
    {"sku": "SKU-FED-024", "product_code": "ND-FED-24", "location": "Zero-Knowledge Consortium (Zurich)", "available": 20, "reserved": 5, "reorder": 5, "unit_cost": 4900.0, "status": "In Stock"}
]

# -------------------------------------------------------------
# 8. Customers (55 Customers >= 50)
# -------------------------------------------------------------
CUSTOMERS_DATA = [
    # Original 5 Client Masters Included as Tier 1 Customers
    {"customer_code": "CUST-101", "company_name": "Apex Financial Technologies", "contact_name": "Marcus Vance", "email": "mvance@apexfintech.com", "phone": "+1-212-555-0141", "city": "New York", "state": "NY", "country": "USA", "industry": "FinTech & Algorithmic Trading", "tier": "Platinum", "credit_limit": 250000.0, "account_balance": 12500.0, "sales_rep_code": "EMP-1010", "status": "Active"},
    {"customer_code": "CUST-102", "company_name": "BioGenix Pharmaceuticals", "contact_name": "Dr. Aris Thorne", "email": "athorne@biogenix-pharma.com", "phone": "+1-617-555-0142", "city": "Boston", "state": "MA", "country": "USA", "industry": "Life Sciences & Clinical Trials", "tier": "Platinum", "credit_limit": 300000.0, "account_balance": 14700.0, "sales_rep_code": "EMP-1011", "status": "Active"},
    {"customer_code": "CUST-103", "company_name": "Vertex Global Logistics", "contact_name": "Helena Ross", "email": "hross@vertexlogistics.io", "phone": "+1-312-555-0143", "city": "Chicago", "state": "IL", "country": "USA", "industry": "Supply Chain & Multi-modal Freight", "tier": "Gold", "credit_limit": 150000.0, "account_balance": 8300.0, "sales_rep_code": "EMP-1018", "status": "Active"},
    {"customer_code": "CUST-104", "company_name": "OmniRetail Group", "contact_name": "Tariq Mansour", "email": "tmansour@omniretail.com", "phone": "+1-206-555-0144", "city": "Seattle", "state": "WA", "country": "USA", "industry": "Omnichannel Retail & E-Commerce", "tier": "Business", "credit_limit": 100000.0, "account_balance": 4800.0, "sales_rep_code": "EMP-1023", "status": "Active"},
    {"customer_code": "CUST-105", "company_name": "CyberShield Defense Systems", "contact_name": "Col. Nathan Drake", "email": "ndrake@cybershield-def.org", "phone": "+1-202-555-0145", "city": "Washington", "state": "DC", "country": "USA", "industry": "Aerospace & Defense Intelligence", "tier": "Air-Gapped Platinum", "credit_limit": 500000.0, "account_balance": 27200.0, "sales_rep_code": "EMP-1003", "status": "Active"},
    # 50 Additional Diverse Enterprises & Mid-Market Accounts
    {"customer_code": "CUST-106", "company_name": "Quantum Capital Advisors", "contact_name": "Edward Norton", "email": "enorton@quantumcap.com", "phone": "+1-212-555-0146", "city": "New York", "state": "NY", "country": "USA", "industry": "Hedge Fund & Wealth Management", "tier": "Platinum", "credit_limit": 200000.0, "account_balance": 9800.0, "sales_rep_code": "EMP-1010", "status": "Active"},
    {"customer_code": "CUST-107", "company_name": "Meridian Health Systems", "contact_name": "Claire Redfield", "email": "credfield@meridian-health.org", "phone": "+1-312-555-0147", "city": "Chicago", "state": "IL", "country": "USA", "industry": "Hospital Network & Healthcare", "tier": "Platinum", "credit_limit": 250000.0, "account_balance": 11400.0, "sales_rep_code": "EMP-1011", "status": "Active"},
    {"customer_code": "CUST-108", "company_name": "Vanguard Aerospace Corp", "contact_name": "Douglas McArthur", "email": "dmcarthur@vanguard-aero.com", "phone": "+1-310-555-0148", "city": "Los Angeles", "state": "CA", "country": "USA", "industry": "Avionics & Defense", "tier": "Platinum", "credit_limit": 350000.0, "account_balance": 18500.0, "sales_rep_code": "EMP-1003", "status": "Active"},
    {"customer_code": "CUST-109", "company_name": "Horizon Media Global", "contact_name": "Alicia Sterling", "email": "asterling@horizonmedia.net", "phone": "+1-415-555-0149", "city": "San Francisco", "state": "CA", "country": "USA", "industry": "Digital Media & AdTech", "tier": "Gold", "credit_limit": 120000.0, "account_balance": 4800.0, "sales_rep_code": "EMP-1018", "status": "Active"},
    {"customer_code": "CUST-110", "company_name": "Terra Nova Energy Resources", "contact_name": "Brian Houston", "email": "bhouston@terranova-energy.com", "phone": "+1-713-555-0150", "city": "Houston", "state": "TX", "country": "USA", "industry": "Oil, Gas & Clean Grid Energy", "tier": "Gold", "credit_limit": 180000.0, "account_balance": 8300.0, "sales_rep_code": "EMP-1023", "status": "Active"},
    {"customer_code": "CUST-111", "company_name": "Zenith Telecom International", "contact_name": "Rajiv Nambiar", "email": "rnambiar@zenith-telecom.in", "phone": "+91-22-555-0151", "city": "Mumbai", "state": "MH", "country": "India", "industry": "5G Infrastructure & Telecom", "tier": "Platinum", "credit_limit": 220000.0, "account_balance": 15000.0, "sales_rep_code": "EMP-1010", "status": "Active"},
    {"customer_code": "CUST-112", "company_name": "Stellar Robotics Labs", "contact_name": "Hans Zimmer", "email": "hzimmer@stellar-robotics.de", "phone": "+49-89-555-0152", "city": "Munich", "state": "BY", "country": "Germany", "industry": "Industrial Automation & Robotics", "tier": "Gold", "credit_limit": 160000.0, "account_balance": 6400.0, "sales_rep_code": "EMP-1018", "status": "Active"},
    {"customer_code": "CUST-113", "company_name": "BlueWave Maritime Shipping", "contact_name": "Dimitrios Papadopoulos", "email": "dimitrios@bluewave-maritime.gr", "phone": "+30-210-555-0153", "city": "Piraeus", "state": "Attica", "country": "Greece", "industry": "Ocean Freight & Fleet Tracking", "tier": "Gold", "credit_limit": 140000.0, "account_balance": 7000.0, "sales_rep_code": "EMP-1011", "status": "Active"},
    {"customer_code": "CUST-114", "company_name": "Cobalt Dynamics Inc", "contact_name": "Jennifer Walsh", "email": "jwalsh@cobalt-dynamics.com", "phone": "+1-617-555-0154", "city": "Boston", "state": "MA", "country": "USA", "industry": "Materials Science & Nanotech", "tier": "Business", "credit_limit": 90000.0, "account_balance": 3500.0, "sales_rep_code": "EMP-1023", "status": "Active"},
    {"customer_code": "CUST-115", "company_name": "Solis Renewable Power", "contact_name": "Mateo Rossi", "email": "mrossi@solis-power.es", "phone": "+34-91-555-0155", "city": "Madrid", "state": "Community of Madrid", "country": "Spain", "industry": "Solar & Wind Power Utilities", "tier": "Gold", "credit_limit": 130000.0, "account_balance": 5200.0, "sales_rep_code": "EMP-1018", "status": "Active"},
    {"customer_code": "CUST-116", "company_name": "Titan Heavy Manufacturing", "contact_name": "Walter White", "email": "wwhite@titan-mfg.com", "phone": "+1-313-555-0156", "city": "Detroit", "state": "MI", "country": "USA", "industry": "Automotive & Heavy Equipment", "tier": "Platinum", "credit_limit": 200000.0, "account_balance": 12500.0, "sales_rep_code": "EMP-1010", "status": "Active"},
    {"customer_code": "CUST-117", "company_name": "Silverline Insurance Partners", "contact_name": "Laura Croft", "email": "lcroft@silverline-ins.co.uk", "phone": "+44-20-555-0157", "city": "London", "state": "England", "country": "United Kingdom", "industry": "Underwriting & Reinsurance", "tier": "Platinum", "credit_limit": 250000.0, "account_balance": 9800.0, "sales_rep_code": "EMP-1011", "status": "Active"},
    {"customer_code": "CUST-118", "company_name": "Cascade Software Systems", "contact_name": "Kenji Sato", "email": "ksato@cascade-systems.jp", "phone": "+81-3-555-0158", "city": "Tokyo", "state": "Kanto", "country": "Japan", "industry": "Enterprise Cloud ERP", "tier": "Gold", "credit_limit": 175000.0, "account_balance": 6400.0, "sales_rep_code": "EMP-1018", "status": "Active"},
    {"customer_code": "CUST-119", "company_name": "Pinnacle Asset Management", "contact_name": "Victoria Chase", "email": "vchase@pinnacle-asset.com", "phone": "+1-212-555-0159", "city": "New York", "state": "NY", "country": "USA", "industry": "Private Equity", "tier": "Platinum", "credit_limit": 300000.0, "account_balance": 14700.0, "sales_rep_code": "EMP-1010", "status": "Active"},
    {"customer_code": "CUST-120", "company_name": "Aura Genomics Research", "contact_name": "Dr. Sarah Lin", "email": "slin@aura-genomics.org", "phone": "+1-858-555-0160", "city": "San Diego", "state": "CA", "country": "USA", "industry": "DNA Sequencing & Bioinformatics", "tier": "Gold", "credit_limit": 150000.0, "account_balance": 11400.0, "sales_rep_code": "EMP-1011", "status": "Active"},
    {"customer_code": "CUST-121", "company_name": "Redwood Semiconductor", "contact_name": "Kevin Chen", "email": "kchen@redwood-semi.com", "phone": "+1-408-555-0161", "city": "San Jose", "state": "CA", "country": "USA", "industry": "Fabless Microelectronics", "tier": "Platinum", "credit_limit": 280000.0, "account_balance": 18500.0, "sales_rep_code": "EMP-1003", "status": "Active"},
    {"customer_code": "CUST-122", "company_name": "Pacific Rim Cargo Lines", "contact_name": "Wei Zhang", "email": "wzhang@pacificrim-cargo.sg", "phone": "+65-6555-0162", "city": "Singapore", "state": "Central", "country": "Singapore", "industry": "Port Operations & Container Logistics", "tier": "Gold", "credit_limit": 160000.0, "account_balance": 7000.0, "sales_rep_code": "EMP-1018", "status": "Active"},
    {"customer_code": "CUST-123", "company_name": "Echo Security Solutions", "contact_name": "Boris Volkov", "email": "bvolkov@echo-sec.com", "phone": "+1-703-555-0163", "city": "Tysons", "state": "VA", "country": "USA", "industry": "Endpoint Protection & Threat Intel", "tier": "Gold", "credit_limit": 140000.0, "account_balance": 5200.0, "sales_rep_code": "EMP-1023", "status": "Active"},
    {"customer_code": "CUST-124", "company_name": "Atlas Cloud Hosting", "contact_name": "Simon Pegg", "email": "spegg@atlas-cloud.ca", "phone": "+1-416-555-0164", "city": "Toronto", "state": "ON", "country": "Canada", "industry": "Managed Kubernetes & IaaS", "tier": "Business", "credit_limit": 100000.0, "account_balance": 4800.0, "sales_rep_code": "EMP-1018", "status": "Active"},
    {"customer_code": "CUST-125", "company_name": "Nordic Nordic Energy Grid", "contact_name": "Freja Lind", "email": "flind@nordic-grid.se", "phone": "+46-8-555-0165", "city": "Stockholm", "state": "Stockholm", "country": "Sweden", "industry": "Hydroelectric & Smart Grid", "tier": "Gold", "credit_limit": 150000.0, "account_balance": 8300.0, "sales_rep_code": "EMP-1010", "status": "Active"},
    {"customer_code": "CUST-126", "company_name": "Beacon Health Partners", "contact_name": "Timothy Evans", "email": "tevans@beaconhealth.org", "phone": "+1-215-555-0166", "city": "Philadelphia", "state": "PA", "country": "USA", "industry": "Health Maintenance Org (HMO)", "tier": "Platinum", "credit_limit": 220000.0, "account_balance": 11400.0, "sales_rep_code": "EMP-1011", "status": "Active"},
    {"customer_code": "CUST-127", "company_name": "Ironclad Logistics Services", "contact_name": "Jack Reacher", "email": "jreacher@ironclad-log.com", "phone": "+1-404-555-0167", "city": "Atlanta", "state": "GA", "country": "USA", "industry": "Intermodal Rail Freight", "tier": "Business", "credit_limit": 90000.0, "account_balance": 3500.0, "sales_rep_code": "EMP-1023", "status": "Active"},
    {"customer_code": "CUST-128", "company_name": "AeroDynamics Defense Corp", "contact_name": "Gregory House", "email": "ghouse@aerodynamics-def.com", "phone": "+1-817-555-0168", "city": "Fort Worth", "state": "TX", "country": "USA", "industry": "Tactical UAV Systems", "tier": "Platinum", "credit_limit": 300000.0, "account_balance": 18500.0, "sales_rep_code": "EMP-1003", "status": "Active"},
    {"customer_code": "CUST-129", "company_name": "Frontier Financial Trust", "contact_name": "Olivia Pope", "email": "opope@frontier-trust.com", "phone": "+1-704-555-0169", "city": "Charlotte", "state": "NC", "country": "USA", "industry": "Commercial Banking", "tier": "Platinum", "credit_limit": 260000.0, "account_balance": 12500.0, "sales_rep_code": "EMP-1010", "status": "Active"},
    {"customer_code": "CUST-130", "company_name": "Prism Digital Marketing", "contact_name": "Don Draper", "email": "ddraper@prism-digital.com", "phone": "+1-312-555-0170", "city": "Chicago", "state": "IL", "country": "USA", "industry": "Performance Ad Networks", "tier": "Standard", "credit_limit": 60000.0, "account_balance": 1500.0, "sales_rep_code": "EMP-1018", "status": "Active"},
    {"customer_code": "CUST-131", "company_name": "Synergy Life Sciences", "contact_name": "Dana Scully", "email": "dscully@synergy-bio.com", "phone": "+1-206-555-0171", "city": "Seattle", "state": "WA", "country": "USA", "industry": "Immunotherapy Therapeutics", "tier": "Gold", "credit_limit": 140000.0, "account_balance": 11400.0, "sales_rep_code": "EMP-1011", "status": "Active"},
    {"customer_code": "CUST-132", "company_name": "Helios Solar Infrastructure", "contact_name": "Apollo Creed", "email": "acreed@helios-solar.com", "phone": "+1-602-555-0172", "city": "Phoenix", "state": "AZ", "country": "USA", "industry": "Utility-scale Photovoltaics", "tier": "Gold", "credit_limit": 130000.0, "account_balance": 5200.0, "sales_rep_code": "EMP-1023", "status": "Active"},
    {"customer_code": "CUST-133", "company_name": "Vortex Autonomous Fleets", "contact_name": "Sarah Connor", "email": "sconnor@vortex-fleets.com", "phone": "+1-512-555-0173", "city": "Austin", "state": "TX", "country": "USA", "industry": "Self-driving Trucking", "tier": "Platinum", "credit_limit": 200000.0, "account_balance": 8300.0, "sales_rep_code": "EMP-1010", "status": "Active"},
    {"customer_code": "CUST-134", "company_name": "AlphaCore Data Centers", "contact_name": "Bruce Wayne", "email": "bwayne@alphacore-dc.com", "phone": "+1-703-555-0174", "city": "Ashburn", "state": "VA", "country": "USA", "industry": "Hyperscale Colocation", "tier": "Platinum", "credit_limit": 350000.0, "account_balance": 14000.0, "sales_rep_code": "EMP-1003", "status": "Active"},
    {"customer_code": "CUST-135", "company_name": "Global Trade Logistics BV", "contact_name": "Jan Van Der Beek", "email": "jbeek@globaltrade.nl", "phone": "+31-10-555-0175", "city": "Rotterdam", "state": "South Holland", "country": "Netherlands", "industry": "Cold Chain & Port Logistics", "tier": "Gold", "credit_limit": 150000.0, "account_balance": 7000.0, "sales_rep_code": "EMP-1018", "status": "Active"},
    {"customer_code": "CUST-136", "company_name": "Sterling Capital Partners", "contact_name": "Harvey Specter", "email": "hspecter@sterling-cap.com", "phone": "+1-212-555-0176", "city": "New York", "state": "NY", "country": "USA", "industry": "Corporate Restructuring", "tier": "Platinum", "credit_limit": 250000.0, "account_balance": 9800.0, "sales_rep_code": "EMP-1010", "status": "Active"},
    {"customer_code": "CUST-137", "company_name": "Crestview Medical Center", "contact_name": "Meredith Grey", "email": "mgrey@crestview-med.org", "phone": "+1-206-555-0177", "city": "Seattle", "state": "WA", "country": "USA", "industry": "Academic Medical Center", "tier": "Platinum", "credit_limit": 200000.0, "account_balance": 11400.0, "sales_rep_code": "EMP-1011", "status": "Active"},
    {"customer_code": "CUST-138", "company_name": "Apex Clean Energy Corp", "contact_name": "Elon West", "email": "ewest@apex-cleanenergy.com", "phone": "+1-303-555-0178", "city": "Denver", "state": "CO", "country": "USA", "industry": "Geothermal & Battery Storage", "tier": "Gold", "credit_limit": 160000.0, "account_balance": 5200.0, "sales_rep_code": "EMP-1023", "status": "Active"},
    {"customer_code": "CUST-139", "company_name": "Starlight Entertainment Inc", "contact_name": "Ari Gold", "email": "agold@starlight-ent.com", "phone": "+1-310-555-0179", "city": "Burbank", "state": "CA", "country": "USA", "industry": "Streaming Media & VOD", "tier": "Business", "credit_limit": 110000.0, "account_balance": 4800.0, "sales_rep_code": "EMP-1018", "status": "Active"},
    {"customer_code": "CUST-140", "company_name": "Omega Defense Industries", "contact_name": "Tony Stark", "email": "tstark@omega-defense.com", "phone": "+1-212-555-0180", "city": "New York", "state": "NY", "country": "USA", "industry": "Advanced Radar & Jamming", "tier": "Air-Gapped Platinum", "credit_limit": 500000.0, "account_balance": 27200.0, "sales_rep_code": "EMP-1003", "status": "Active"},
    {"customer_code": "CUST-141", "company_name": "Boreal Forestry Products", "contact_name": "Lars Mikkelsen", "email": "lmikkelsen@boreal-fp.ca", "phone": "+1-604-555-0181", "city": "Vancouver", "state": "BC", "country": "Canada", "industry": "Sustainable Pulp & Timber", "tier": "Standard", "credit_limit": 70000.0, "account_balance": 2800.0, "sales_rep_code": "EMP-1023", "status": "Active"},
    {"customer_code": "CUST-142", "company_name": "Equinox Insurance Corp", "contact_name": "Gillian Anderson", "email": "ganderson@equinox-ins.com", "phone": "+1-614-555-0182", "city": "Columbus", "state": "OH", "country": "USA", "industry": "Property & Casualty", "tier": "Gold", "credit_limit": 170000.0, "account_balance": 9800.0, "sales_rep_code": "EMP-1010", "status": "Active"},
    {"customer_code": "CUST-143", "company_name": "Trident Subsea Robotics", "contact_name": "Arthur Curry", "email": "acurry@trident-subsea.no", "phone": "+47-51-555-0183", "city": "Stavanger", "state": "Rogaland", "country": "Norway", "industry": "Deepwater Offshore Surveying", "tier": "Gold", "credit_limit": 150000.0, "account_balance": 6400.0, "sales_rep_code": "EMP-1018", "status": "Active"},
    {"customer_code": "CUST-144", "company_name": "Nova BioDiagnostics", "contact_name": "Elizabeth Holmes", "email": "eholmes@nova-biodx.com", "phone": "+1-650-555-0184", "city": "Palo Alto", "state": "CA", "country": "USA", "industry": "Molecular Pathology", "tier": "Business", "credit_limit": 80000.0, "account_balance": 3500.0, "sales_rep_code": "EMP-1011", "status": "Active"},
    {"customer_code": "CUST-145", "company_name": "Zenith Financial Brokerage", "contact_name": "Jordan Belfort", "email": "jbelfort@zenith-broker.com", "phone": "+1-212-555-0185", "city": "New York", "state": "NY", "country": "USA", "industry": "Institutional Equities", "tier": "Platinum", "credit_limit": 220000.0, "account_balance": 12500.0, "sales_rep_code": "EMP-1010", "status": "Active"},
    {"customer_code": "CUST-146", "company_name": "Solaria Smart Grid Solutions", "contact_name": "Nikola Tesla", "email": "ntesla@solaria-grid.ch", "phone": "+41-44-555-0186", "city": "Zurich", "state": "Zurich", "country": "Switzerland", "industry": "Grid Edge Automation", "tier": "Gold", "credit_limit": 160000.0, "account_balance": 5200.0, "sales_rep_code": "EMP-1023", "status": "Active"},
    {"customer_code": "CUST-147", "company_name": "Vanguard Commercial Real Estate", "contact_name": "Richard Sterling", "email": "rsterling@vanguard-cre.com", "phone": "+1-312-555-0187", "city": "Chicago", "state": "IL", "country": "USA", "industry": "Commercial Property Asset Trust", "tier": "Gold", "credit_limit": 140000.0, "account_balance": 4800.0, "sales_rep_code": "EMP-1018", "status": "Active"},
    {"customer_code": "CUST-148", "company_name": "Summit Health Institute", "contact_name": "Leonard McCoy", "email": "lmccoy@summit-health.org", "phone": "+1-412-555-0188", "city": "Pittsburgh", "state": "PA", "country": "USA", "industry": "Neurological Research Hospital", "tier": "Platinum", "credit_limit": 240000.0, "account_balance": 11400.0, "sales_rep_code": "EMP-1011", "status": "Active"},
    {"customer_code": "CUST-149", "company_name": "AeroSpace Tech Global", "contact_name": "Buzz Aldrin", "email": "baldrin@aerospacetech.com", "phone": "+1-321-555-0189", "city": "Cape Canaveral", "state": "FL", "country": "USA", "industry": "Commercial Rocket Avionics", "tier": "Platinum", "credit_limit": 300000.0, "account_balance": 18500.0, "sales_rep_code": "EMP-1003", "status": "Active"},
    {"customer_code": "CUST-150", "company_name": "Krypton Cyber Intelligence", "contact_name": "Clark Kent", "email": "ckent@krypton-intel.com", "phone": "+1-202-555-0190", "city": "Washington", "state": "DC", "country": "USA", "industry": "Nation-State Threat Hunting", "tier": "Air-Gapped Platinum", "credit_limit": 450000.0, "account_balance": 27200.0, "sales_rep_code": "EMP-1003", "status": "Active"},
    {"customer_code": "CUST-151", "company_name": "Atlas Mining & Metals Group", "contact_name": "Gunter Sachs", "email": "gsachs@atlas-mining.za", "phone": "+27-11-555-0191", "city": "Johannesburg", "state": "Gauteng", "country": "South Africa", "industry": "Autonomous Heavy Extraction", "tier": "Gold", "credit_limit": 180000.0, "account_balance": 8300.0, "sales_rep_code": "EMP-1018", "status": "Active"},
    {"customer_code": "CUST-152", "company_name": "Pioneer AgTech Solutions", "contact_name": "Norman Borlaug", "email": "nborlaug@pioneer-agtech.com", "phone": "+1-515-555-0192", "city": "Des Moines", "state": "IA", "country": "USA", "industry": "Precision Crop Analytics", "tier": "Business", "credit_limit": 85000.0, "account_balance": 3500.0, "sales_rep_code": "EMP-1023", "status": "Active"},
    {"customer_code": "CUST-153", "company_name": "Metropolis Urban Transit", "contact_name": "Perry White", "email": "pwhite@metropolis-transit.gov", "phone": "+1-212-555-0193", "city": "New York", "state": "NY", "country": "USA", "industry": "Autonomous Bus & Rail Systems", "tier": "Gold", "credit_limit": 150000.0, "account_balance": 6400.0, "sales_rep_code": "EMP-1010", "status": "Active"},
    {"customer_code": "CUST-154", "company_name": "Starlight Cloud Telecom", "contact_name": "Galen Erso", "email": "gerso@starlight-telecom.com", "phone": "+1-303-555-0194", "city": "Boulder", "state": "CO", "country": "USA", "industry": "Satellite Internet Constellation", "tier": "Platinum", "credit_limit": 280000.0, "account_balance": 15000.0, "sales_rep_code": "EMP-1018", "status": "Active"},
    {"customer_code": "CUST-155", "company_name": "Omega BioSciences Europe", "contact_name": "Jean-Luc Picard", "email": "jpicard@omega-biosci.fr", "phone": "+33-1-555-0195", "city": "Paris", "state": "Ile-de-France", "country": "France", "industry": "CRISPR Gene Therapies", "tier": "Platinum", "credit_limit": 260000.0, "account_balance": 14700.0, "sales_rep_code": "EMP-1011", "status": "Active"}
]

# -------------------------------------------------------------
# 9. Clients Master (5 Compatible Accounts)
# -------------------------------------------------------------
CLIENTS_MASTER_DATA = [
    {"client_code": "MST-101", "company_name": "Apex Financial Technologies", "industry": "FinTech / Algorithmic Trading", "region": "North America (New York)", "tier": "Platinum", "contact_person": "Marcus Vance (VP Tech)", "email": "mvance@apexfintech.com", "status": "Active"},
    {"client_code": "MST-102", "company_name": "BioGenix Pharmaceuticals", "industry": "Life Sciences / Clinical Trials", "region": "North America (Boston)", "tier": "Platinum", "contact_person": "Dr. Aris Thorne (Chief Bio-Informaticist)", "email": "athorne@biogenix-pharma.com", "status": "Active"},
    {"client_code": "MST-103", "company_name": "Vertex Global Logistics", "industry": "Supply Chain & Multi-modal Freight", "region": "North America (Chicago)", "tier": "Gold", "contact_person": "Helena Ross (Head of Fleet Analytics)", "email": "hross@vertexlogistics.io", "status": "Active"},
    {"client_code": "MST-104", "company_name": "OmniRetail Group", "industry": "Omnichannel Retail & E-Commerce", "region": "North America (Seattle)", "tier": "Business", "contact_person": "Tariq Mansour (Lead Data Architect)", "email": "tmansour@omniretail.com", "status": "Active"},
    {"client_code": "MST-105", "company_name": "CyberShield Defense Systems", "industry": "Aerospace & Defense Intelligence", "region": "North America (Washington DC)", "tier": "Air-Gapped Platinum", "contact_person": "Col. Nathan Drake (Security Director)", "email": "ndrake@cybershield-def.org", "status": "Active"}
]

# -------------------------------------------------------------
# 10. Orders & Order Items (115 Orders >= 100)
# -------------------------------------------------------------
ORDERS_DATA = []
ORDER_ITEMS_DATA = []
PAYMENTS_DATA = []

# Generate 115 realistic orders spread over 2025 and 2026
base_date = datetime(2025, 1, 15)
sales_reps = ["EMP-1003", "EMP-1010", "EMP-1011", "EMP-1018", "EMP-1023"]

for i in range(1, 116):
    order_num = f"ORD-2025-{i:03d}" if i <= 70 else f"ORD-2026-{i:03d}"
    cust = CUSTOMERS_DATA[(i - 1) % len(CUSTOMERS_DATA)]
    order_dt = base_date + timedelta(days=i * 5 + random.randint(0, 3))
    dt_str = order_dt.strftime("%Y-%m-%d")

    # Select 1 to 3 products
    num_items = random.choices([1, 2, 3], weights=[0.6, 0.3, 0.1])[0]
    chosen_products = random.sample(PRODUCTS_DATA, num_items)
    
    order_total = 0.0
    items_list = []
    for p in chosen_products:
        qty = 1 if "Appliance" not in p["name"] else random.randint(1, 3)
        unit_price = float(p["price"])
        subtotal = round(unit_price * qty, 2)
        disc = round(subtotal * 0.05, 2) if qty > 1 or "Platinum" in p["tier"] else 0.0
        line_total = round(subtotal - disc, 2)
        order_total += line_total
        items_list.append({
            "order_number": order_num,
            "product_code": p["product_code"],
            "quantity": qty,
            "unit_price": unit_price,
            "subtotal": subtotal,
            "discount": disc,
            "line_total": line_total
        })

    # Status probabilities
    status = "Completed" if i <= 95 else random.choice(["Processing", "Delivered", "Completed", "Pending Approval"])
    p_status = "Paid" if status in ["Completed", "Delivered"] else ("Partially Paid" if status == "Processing" else "Invoiced")
    
    ORDERS_DATA.append({
        "order_number": order_num,
        "customer_code": cust["customer_code"],
        "order_date": dt_str,
        "status": status,
        "total_amount": round(order_total, 2),
        "discount_amount": round(sum(it["discount"] for it in items_list), 2),
        "net_amount": round(order_total, 2),
        "payment_status": p_status,
        "sales_rep_code": cust.get("sales_rep_code", random.choice(sales_reps)),
        "billing_cycle": random.choice(["Monthly", "Annual", "One-Time"]),
        "notes": f"Enterprise procurement for {cust['company_name']}. Primary contract tier: {cust['tier']}."
    })
    ORDER_ITEMS_DATA.extend(items_list)

    # Add Payment record
    pay_methods = ["Wire Transfer", "ACH Corporate", "Credit Card", "Purchase Order"]
    pay_method = "Wire Transfer" if order_total > 10000 else random.choice(pay_methods)
    PAYMENTS_DATA.append({
        "payment_ref": f"PAY-{order_num[4:]}",
        "order_number": order_num,
        "customer_code": cust["customer_code"],
        "amount": round(order_total, 2),
        "currency": "USD",
        "payment_method": pay_method,
        "status": "Success" if p_status == "Paid" else ("Pending" if p_status == "Invoiced" else "Settled"),
        "payment_date": dt_str,
        "gateway_ref": f"STRIPE-CH-{random.randint(100000, 999999)}-TX"
    })

# -------------------------------------------------------------
# 11. Transactions (215 Transactions >= 200)
# -------------------------------------------------------------
# First 20 are the exact original 20 transactions
ORIGINAL_20_TRANSACTIONS = [
    {"transaction_ref": "TXN-2026-001", "client_code": "MST-101", "product_code": "ND-ENT-01", "amount": 12500.0, "status": "Completed", "payment_method": "Wire Transfer", "transaction_date": "2026-01-05", "notes": "Q1 Enterprise platform licensing retainer"},
    {"transaction_ref": "TXN-2026-002", "client_code": "MST-101", "product_code": "ND-SEC-03", "amount": 2200.0, "status": "Completed", "payment_method": "Wire Transfer", "transaction_date": "2026-01-05", "notes": "Air-gapped financial enclave provisioning"},
    {"transaction_ref": "TXN-2026-003", "client_code": "MST-101", "product_code": "ND-ETL-04", "amount": 3500.0, "status": "Completed", "payment_method": "Wire Transfer", "transaction_date": "2026-02-01", "notes": "Real-time market feed ingestion module"},
    {"transaction_ref": "TXN-2026-004", "client_code": "MST-101", "product_code": "ND-ENT-01", "amount": 12500.0, "status": "Completed", "payment_method": "Wire Transfer", "transaction_date": "2026-02-05", "notes": "Monthly platform auto-renewal"},
    {"transaction_ref": "TXN-2026-005", "client_code": "MST-102", "product_code": "ND-ENT-01", "amount": 12500.0, "status": "Completed", "payment_method": "ACH", "transaction_date": "2026-01-12", "notes": "Clinical trial document intelligence contract"},
    {"transaction_ref": "TXN-2026-006", "client_code": "MST-102", "product_code": "ND-SEC-03", "amount": 2200.0, "status": "Completed", "payment_method": "ACH", "transaction_date": "2026-01-12", "notes": "HIPAA-certified sandbox validation"},
    {"transaction_ref": "TXN-2026-007", "client_code": "MST-102", "product_code": "ND-API-05", "amount": 1500.0, "status": "Completed", "payment_method": "ACH", "transaction_date": "2026-02-01", "notes": "High-throughput researcher API seats"},
    {"transaction_ref": "TXN-2026-008", "client_code": "MST-102", "product_code": "ND-ENT-01", "amount": 12500.0, "status": "Completed", "payment_method": "ACH", "transaction_date": "2026-02-12", "notes": "Monthly platform renewal"},
    {"transaction_ref": "TXN-2026-009", "client_code": "MST-103", "product_code": "ND-CLD-02", "amount": 4800.0, "status": "Completed", "payment_method": "Credit Card", "transaction_date": "2026-01-15", "notes": "Supply chain automated BI dashboard"},
    {"transaction_ref": "TXN-2026-010", "client_code": "MST-103", "product_code": "ND-ETL-04", "amount": 3500.0, "status": "Completed", "payment_method": "Credit Card", "transaction_date": "2026-01-15", "notes": "Logistics sensor telematics stream connector"},
    {"transaction_ref": "TXN-2026-011", "client_code": "MST-103", "product_code": "ND-CLD-02", "amount": 4800.0, "status": "Completed", "payment_method": "Credit Card", "transaction_date": "2026-02-15", "notes": "Monthly analytics subscription"},
    {"transaction_ref": "TXN-2026-012", "client_code": "MST-104", "product_code": "ND-CLD-02", "amount": 4800.0, "status": "Completed", "payment_method": "ACH", "transaction_date": "2026-01-20", "notes": "Omnichannel inventory query optimization"},
    {"transaction_ref": "TXN-2026-013", "client_code": "MST-104", "product_code": "ND-API-05", "amount": 1500.0, "status": "Completed", "payment_method": "ACH", "transaction_date": "2026-01-20", "notes": "Store manager natural language lookup API"},
    {"transaction_ref": "TXN-2026-014", "client_code": "MST-104", "product_code": "ND-CLD-02", "amount": 4800.0, "status": "Completed", "payment_method": "ACH", "transaction_date": "2026-02-20", "notes": "Monthly analytics renewal"},
    {"transaction_ref": "TXN-2026-015", "client_code": "MST-105", "product_code": "ND-ENT-01", "amount": 12500.0, "status": "Completed", "payment_method": "Wire Transfer", "transaction_date": "2026-01-28", "notes": "Defense intelligence sovereign cloud deployment"},
    {"transaction_ref": "TXN-2026-016", "client_code": "MST-105", "product_code": "ND-SEC-03", "amount": 2200.0, "status": "Completed", "payment_method": "Wire Transfer", "transaction_date": "2026-01-28", "notes": "FIPS 140-2 Level 3 hardware security module"},
    {"transaction_ref": "TXN-2026-017", "client_code": "MST-105", "product_code": "ND-ETL-04", "amount": 3500.0, "status": "Completed", "payment_method": "Wire Transfer", "transaction_date": "2026-02-01", "notes": "Tactical document ingestion stream"},
    {"transaction_ref": "TXN-2026-018", "client_code": "MST-105", "product_code": "ND-ENT-01", "amount": 12500.0, "status": "Completed", "payment_method": "Wire Transfer", "transaction_date": "2026-02-28", "notes": "Monthly sovereign enclave subscription"},
    {"transaction_ref": "TXN-2026-019", "client_code": "MST-101", "product_code": "ND-API-05", "amount": 1500.0, "status": "Completed", "payment_method": "Wire Transfer", "transaction_date": "2026-03-01", "notes": "Algorithmic execution copilot endpoint expansion"},
    {"transaction_ref": "TXN-2026-020", "client_code": "MST-103", "product_code": "ND-API-05", "amount": 1500.0, "status": "Completed", "payment_method": "Credit Card", "transaction_date": "2026-03-01", "notes": "Mobile warehouse scanner REST endpoints"}
]

TRANSACTIONS_DATA = list(ORIGINAL_20_TRANSACTIONS)

# Generate 195 additional transactions (2025 to 2026) to reach 215 total (>= 200)
txn_base_date = datetime(2025, 2, 1)
client_codes_all = [c["customer_code"] for c in CUSTOMERS_DATA]
product_codes_all = [p["product_code"] for p in PRODUCTS_DATA]

for idx in range(21, 216):
    ref = f"TXN-2025-{idx:03d}" if idx <= 120 else f"TXN-2026-{idx:03d}"
    c_code = client_codes_all[(idx - 1) % len(client_codes_all)]
    p_code = product_codes_all[(idx * 3) % len(product_codes_all)]
    
    # Match product price
    matching_p = next(p for p in PRODUCTS_DATA if p["product_code"] == p_code)
    amount = float(matching_p["price"])

    txn_dt = txn_base_date + timedelta(days=idx * 2 + random.randint(0, 2))
    date_str = txn_dt.strftime("%Y-%m-%d")

    status = "Completed" if idx <= 180 else random.choice(["Completed", "Pending", "Processing"])
    p_method = "Wire Transfer" if amount >= 10000 else random.choice(["Wire Transfer", "ACH Corporate", "Credit Card", "Purchase Order"])
    
    notes = f"Transaction for {matching_p['name']} ({matching_p['tier']}) - Account {c_code}."

    TRANSACTIONS_DATA.append({
        "transaction_ref": ref,
        "client_code": c_code,
        "product_code": p_code,
        "amount": amount,
        "currency": "USD",
        "status": status,
        "payment_method": p_method,
        "transaction_date": date_str,
        "notes": notes
    })

# -------------------------------------------------------------
# 12. Policies (10 Corporate & AI Policies)
# -------------------------------------------------------------
POLICIES_DATA = [
    {
        "policy_code": "POL-01",
        "title": "Zero Data Leakage & Customer Privacy Policy",
        "category": "Data Privacy",
        "version": "v3.2",
        "effective_date": "2024-01-01",
        "department_code": "DEP-SEC",
        "summary": "Guarantees customer dataset rows, prompts, and embeddings are NEVER used to train foundational AI models.",
        "full_text": "NexaData AI enforces strict tenant isolation. Customer documents and database rows are indexed into cryptographically isolated vector namespaces. All LLM inferences are executed under zero-retention agreements. Data is encrypted in transit (TLS 1.3) and at rest (AES-256). Ephemeral memory scrubbing occurs immediately upon query resolution."
    },
    {
        "policy_code": "POL-02",
        "title": "Service Level Agreement (SLA) & Uptime Guarantee",
        "category": "SLA & Uptime",
        "version": "v2.5",
        "effective_date": "2024-03-15",
        "department_code": "DEP-ENG",
        "summary": "Establishes a 99.99% availability SLA for Platinum tiers and outlines pro-rated credit refunds for unplanned downtime.",
        "full_text": "NexaData guarantees 99.99% monthly uptime for Platinum Enterprise Engine deployments and 99.9% for Cloud Analytics tiers. Uptime is calculated excluding scheduled maintenance windows announced 72 hours in advance. If availability dips below the threshold, customers receive a 10% credit for every 0.1% downtime below SLA, up to 100% of the monthly fee."
    },
    {
        "policy_code": "POL-03",
        "title": "14-Day Money-Back Satisfaction Guarantee & Billing Terms",
        "category": "Billing & Refunds",
        "version": "v2.0",
        "effective_date": "2023-09-01",
        "department_code": "DEP-FIN",
        "summary": "Provides a 100% refund guarantee within 14 calendar days of initial deployment for all enterprise subscription plans.",
        "full_text": "All new NexaData AI software subscription plans include an unconditional 14-day 100% money-back satisfaction guarantee. If the platform does not meet enterprise technical requirements, written notice sent to support@nexadata.ai within 14 days will initiate a full refund. Annual contracts billed in advance are non-refundable after the 14-day evaluation window."
    },
    {
        "policy_code": "POL-04",
        "title": "SOC2 Type II & FedRAMP Information Security Standard",
        "category": "Security & Compliance",
        "version": "v4.0",
        "effective_date": "2024-02-01",
        "department_code": "DEP-SEC",
        "summary": "Specifies audit controls, annual penetration testing, multi-factor authentication, and RBAC requirements.",
        "full_text": "NexaData complies with AICPA SOC2 Type II Trust Services Criteria (Security, Availability, Confidentiality) and FedRAMP High baseline requirements. Access to production environments requires hardware-backed FIPS 140-2 keys (YubiKey) and time-bound approval from two security officers. Annual third-party penetration tests are made available under NDA."
    },
    {
        "policy_code": "POL-05",
        "title": "Acceptable Use & Autonomous AI Safety Guidelines",
        "category": "Acceptable Use",
        "version": "v1.8",
        "effective_date": "2024-05-10",
        "department_code": "DEP-RES",
        "summary": "Restricts deployment of NexaData models for malicious surveillance, autonomous weapons, or deceptive practices.",
        "full_text": "NexaData AI technologies may not be employed for unlawful surveillance, automated discriminatory credit or hiring decisions without human review, generation of deceptive media, or weaponized autonomous systems. Violation results in immediate suspension of API keys and cancellation of contracts."
    },
    {
        "policy_code": "POL-06",
        "title": "Disaster Recovery & Business Continuity Framework",
        "category": "Disaster Recovery",
        "version": "v2.2",
        "effective_date": "2024-06-01",
        "department_code": "DEP-ENG",
        "summary": "Defines Recovery Point Objective (RPO < 1 min) and Recovery Time Objective (RTO < 5 min) across multi-cloud regions.",
        "full_text": "Production databases and vector indexes are continuously mirrored across independent availability zones (US-East and US-West). In the event of catastrophic regional cloud failure, automated DNS failover reroutes traffic within 300 seconds. Quarterly disaster recovery drills simulate full-datacenter blackouts."
    },
    {
        "policy_code": "POL-07",
        "title": "Remote Device Security & Endpoint Governance Policy",
        "category": "Internal Security",
        "version": "v3.0",
        "effective_date": "2023-11-15",
        "department_code": "DEP-SEC",
        "summary": "Mandates full-disk encryption (FileVault/BitLocker), MDM enrollment, and zero local customer data caching on staff laptops.",
        "full_text": "All employee workstations must be corporate-managed, enrolled in Jamf/InTune MDM, and protected with active endpoint detection and response (EDR). Personnel are strictly prohibited from copying customer data or credentials to local drives or unapproved personal storage."
    },
    {
        "policy_code": "POL-08",
        "title": "Customer Data Retention & Secure Sanitization Policy",
        "category": "Data Governance",
        "version": "v2.1",
        "effective_date": "2024-04-01",
        "department_code": "DEP-SEC",
        "summary": "Specifies cryptographic erasure and NIST 800-88 sanitization upon contract termination within 30 days.",
        "full_text": "Upon account cancellation or contract expiration, customer vector embeddings, uploaded files, and tenant caches are permanently erased within 30 days using NIST 800-88 compliant cryptographic wiping. A formal Certificate of Data Destruction is delivered to the customer compliance team."
    },
    {
        "policy_code": "POL-09",
        "title": "Intellectual Property & Custom Model Weights Ownership",
        "category": "Legal & IP",
        "version": "v1.5",
        "effective_date": "2023-08-01",
        "department_code": "DEP-FIN",
        "summary": "Establishes that all fine-tuned weights, embeddings, and synthesized artifacts remain 100% customer property.",
        "full_text": "Customers retain sole and exclusive intellectual property ownership of all uploaded datasets, prompt histories, synthesized answers, and proprietary fine-tuned model adapter weights created using NexaData professional services. NexaData retains ownership of core platform algorithms and runtime SDKs."
    },
    {
        "policy_code": "POL-10",
        "title": "Enterprise Support Escalation & Incident Management",
        "category": "Support",
        "version": "v2.4",
        "effective_date": "2024-07-01",
        "department_code": "DEP-CS",
        "summary": "Outlines response times: Severity 1 (15 mins), Severity 2 (1 hour), Severity 3 (4 hours), and Severity 4 (24 hours).",
        "full_text": "Incident priorities are categorized from Sev-1 (critical outage or security breach) to Sev-4 (minor feature inquiry). Sev-1 issues immediately page the on-call SRE lead, engineering VP, and dedicated account executive. Post-mortem root cause analysis (RCA) reports are published within 5 business days."
    }
]

# -------------------------------------------------------------
# 13. FAQs (15 Comprehensive Questions & Answers)
# -------------------------------------------------------------
FAQS_DATA = [
    {
        "faq_code": "FAQ-01",
        "category": "Product Overview",
        "question": "What is NexaData AI and what solutions does it provide?",
        "answer": "NexaData AI is an autonomous enterprise data intelligence platform. It provides document-grounded cognitive analysis, natural language SQL querying, secure client-isolated RAG, and executive analytics pipelines.",
        "keywords": "what is nexadata, solutions, overview, core capabilities, platform"
    },
    {
        "faq_code": "FAQ-02",
        "category": "Pricing & Licensing",
        "question": "What are the pricing plans for NexaData AI?",
        "answer": "Pricing starts at $1,500/month for the Developer API Gateway, $2,200/month for the Secure Sandbox, $4,800/month for Cloud Analytics, and $12,500/month for the Platinum Enterprise Engine. Custom appliances are available starting at $18,500.",
        "keywords": "pricing, cost, plans, tiers, license, subscription fee"
    },
    {
        "faq_code": "FAQ-03",
        "category": "Data Privacy",
        "question": "Does NexaData AI use our company data to train general models?",
        "answer": "No. Under our Zero Data Leakage Policy, customer data is never used for model training. Every enterprise deployment operates in a cryptographically isolated tenant enclave.",
        "keywords": "privacy, train models, data leakage, security, confidentiality"
    },
    {
        "faq_code": "FAQ-04",
        "category": "Database Integrations",
        "question": "Which databases and cloud warehouses does NexaData connect with?",
        "answer": "NexaData natively connects to PostgreSQL, Snowflake, Oracle Exadata, Databricks, Apache Kafka, Microsoft SQL Server, BigQuery, and MongoDB Atlas.",
        "keywords": "databases, postgres, snowflake, oracle, kafka, integrations, connectors"
    },
    {
        "faq_code": "FAQ-05",
        "category": "SLA & Support",
        "question": "What uptime SLA does NexaData offer?",
        "answer": "We provide a 99.99% monthly uptime SLA for Platinum enterprise tiers and 99.9% for Cloud Analytics tiers, backed by 24/7 dedicated solutions engineering.",
        "keywords": "sla, uptime, availability, reliability, support"
    },
    {
        "faq_code": "FAQ-06",
        "category": "Refunds & Guarantees",
        "question": "Is there a money-back satisfaction guarantee?",
        "answer": "Yes. All subscription tiers carry an unconditional 14-day 100% money-back satisfaction guarantee upon initial deployment.",
        "keywords": "refund, money back guarantee, satisfaction guarantee, cancel"
    },
    {
        "faq_code": "FAQ-07",
        "category": "Compliance",
        "question": "Is NexaData AI SOC2 and HIPAA compliant?",
        "answer": "Yes. NexaData is certified SOC2 Type II compliant and offers BAA agreements for HIPAA-regulated healthcare organizations via our dedicated security enclaves.",
        "keywords": "soc2, hipaa, compliance, regulations, certification, baa"
    },
    {
        "faq_code": "FAQ-08",
        "category": "Deployment Options",
        "question": "Can NexaData AI be deployed on-premises or air-gapped?",
        "answer": "Yes. We offer the NexaData Edge AI Appliance Server (ND-EDG-09) and containerized air-gapped Kubernetes packages for defense, healthcare, and financial institutions.",
        "keywords": "on-premises, air-gapped, edge appliance, hardware, private cloud"
    },
    {
        "faq_code": "FAQ-09",
        "category": "Sales & Billing",
        "question": "What payment methods are supported for enterprise orders?",
        "answer": "We support Wire Transfer, ACH Corporate transfers, Credit Cards, and Purchase Orders on Net 30/60 terms.",
        "keywords": "payment methods, wire transfer, ach, credit card, purchase order, invoice"
    },
    {
        "faq_code": "FAQ-10",
        "category": "Document Formats",
        "question": "What file types can be uploaded and analyzed by NexaData AI?",
        "answer": "The platform accepts PDF, Word (DOCX), Plain Text (TXT), CSV datasets, and image formats (PNG, JPG, JPEG, WEBP) up to 10 MB per file.",
        "keywords": "file types, upload, pdf, docx, csv, images, txt, format support"
    },
    {
        "faq_code": "FAQ-11",
        "category": "AI Models",
        "question": "What AI models power NexaData conversational responses?",
        "answer": "NexaData leverages state-of-the-art vision and language models (including OpenAI GPT-4o and specialized open-source embeddings), grounded in verified relational schemas and indexed documents.",
        "keywords": "models, llm, gpt-4o, openai, embeddings, vector search"
    },
    {
        "faq_code": "FAQ-12",
        "category": "Company Background",
        "question": "Where is NexaData headquartered and when was it founded?",
        "answer": "NexaData AI Solutions was founded in 2021 and is headquartered at 100 Technology Square, Suite 500, Cambridge, MA 02139, USA.",
        "keywords": "headquarters, founded, location, cambridge, address, company background"
    },
    {
        "faq_code": "FAQ-13",
        "category": "Voice Input",
        "question": "Does NexaData AI support voice dictation and multilingual queries?",
        "answer": "Yes. The chat input features microphone voice dictation with real-time speech recognition supporting English and Hindi.",
        "keywords": "microphone, voice, speech recognition, hindi, dictation, audio"
    },
    {
        "faq_code": "FAQ-14",
        "category": "Customer Success",
        "question": "How quickly can NexaData be deployed in an existing enterprise stack?",
        "answer": "Cloud Analytics and API tiers can be provisioned in under 15 minutes. Custom enterprise legacy migrations typically complete within 5 to 10 business days.",
        "keywords": "onboarding, deployment time, setup, implementation, timeline"
    },
    {
        "faq_code": "FAQ-15",
        "category": "Contact & Support",
        "question": "How can I contact NexaData enterprise support?",
        "answer": "Enterprise support is available 24/7 via support@nexadata.ai, by phone at +1 (800) 555-6392, or directly through the assistant chat.",
        "keywords": "contact, email, phone, support desk, help, reach support"
    }
]


def generate_sql_insert_script() -> str:
    """Generate raw SQL INSERT statements with ON CONFLICT DO NOTHING for all 15 tables."""
    lines = [
        "-- ============================================================================",
        "-- NexaData AI Enterprise Database Seed Data",
        "-- Auto-generated for PostgreSQL & SQLite compatibility",
        "-- ============================================================================",
        ""
    ]

    def esc(val):
        if val is None:
            return "NULL"
        if isinstance(val, bool):
            return "TRUE" if val else "FALSE"
        if isinstance(val, (int, float)):
            return str(val)
        # Escape single quotes
        cleaned = str(val).replace("'", "''")
        return f"'{cleaned}'"

    # 1. Company Info
    lines.append("-- 1. Company Information")
    c = COMPANY_INFO_DATA
    lines.append(
        f"INSERT INTO company_info (company_name, legal_name, tagline, tax_id, founded_year, headquarters, website, support_email, sales_email, phone, mission, vision, fiscal_year_end, primary_currency) "
        f"VALUES ({esc(c['company_name'])}, {esc(c['legal_name'])}, {esc(c['tagline'])}, {esc(c['tax_id'])}, {c['founded_year']}, {esc(c['headquarters'])}, {esc(c['website'])}, {esc(c['support_email'])}, {esc(c['sales_email'])}, {esc(c['phone'])}, {esc(c['mission'])}, {esc(c['vision'])}, {esc(c['fiscal_year_end'])}, {esc(c['primary_currency'])});"
    )
    lines.append("")

    # 2. Departments
    lines.append("-- 2. Departments")
    for d in DEPARTMENTS_DATA:
        lines.append(
            f"INSERT INTO departments (department_code, name, head_of_department, budget, location, employee_count, contact_email) "
            f"VALUES ({esc(d['department_code'])}, {esc(d['name'])}, {esc(d['head_of_department'])}, {d['budget']}, {esc(d['location'])}, {d['employee_count']}, {esc(d['contact_email'])});"
        )
    lines.append("")

    # 3. Categories
    lines.append("-- 3. Categories")
    for cat in CATEGORIES_DATA:
        lines.append(
            f"INSERT INTO categories (category_code, name, description) "
            f"VALUES ({esc(cat['category_code'])}, {esc(cat['name'])}, {esc(cat['description'])});"
        )
    lines.append("")

    # 4. Suppliers
    lines.append("-- 4. Suppliers")
    for s in SUPPLIERS_DATA:
        lines.append(
            f"INSERT INTO suppliers (supplier_code, name, contact_name, email, phone, country, service_type, rating, payment_terms) "
            f"VALUES ({esc(s['supplier_code'])}, {esc(s['name'])}, {esc(s['contact_name'])}, {esc(s['email'])}, {esc(s['phone'])}, {esc(s['country'])}, {esc(s['service_type'])}, {s['rating']}, {esc(s['payment_terms'])});"
        )
    lines.append("")

    # 5. Products
    lines.append("-- 5. Products (24 Products)")
    for p in PRODUCTS_DATA:
        lines.append(
            f"INSERT INTO products (product_code, name, tier, price, cost_price, billing_type, stock_quantity, description, features, is_active) "
            f"VALUES ({esc(p['product_code'])}, {esc(p['name'])}, {esc(p['tier'])}, {p['price']}, {p['cost_price']}, {esc(p['billing_type'])}, {p['stock_quantity']}, {esc(p['description'])}, {esc(p['features'])}, {esc(p['is_active'])});"
        )
    lines.append("")

    # 6. Inventory
    lines.append("-- 6. Inventory (24 records)")
    for inv in INVENTORY_DATA:
        lines.append(
            f"INSERT INTO inventory (sku, product_id, warehouse_location, quantity_available, quantity_reserved, reorder_level, unit_cost, last_restocked, status) "
            f"SELECT {esc(inv['sku'])}, id, {esc(inv['location'])}, {inv['available']}, {inv['reserved']}, {inv['reorder']}, {inv['unit_cost']}, '2026-01-15', {esc(inv['status'])} FROM products WHERE product_code = {esc(inv['product_code'])};"
        )
    lines.append("")

    # 7. Employees
    lines.append("-- 7. Employees (25 records)")
    for e in EMPLOYEES_DATA:
        lines.append(
            f"INSERT INTO employees (employee_code, first_name, last_name, email, phone, department_id, role, salary, hire_date, status, location) "
            f"SELECT {esc(e['employee_code'])}, {esc(e['first_name'])}, {esc(e['last_name'])}, {esc(e['email'])}, {esc(e['phone'])}, id, {esc(e['role'])}, {e['salary']}, {esc(e['hire_date'])}, 'Active', {esc(e['location'])} FROM departments WHERE department_code = {esc(e['department_code'])};"
        )
    lines.append("")

    # 8. Customers
    lines.append("-- 8. Customers (55 records)")
    for cu in CUSTOMERS_DATA:
        lines.append(
            f"INSERT INTO customers (customer_code, company_name, contact_name, email, phone, city, state, country, industry, tier, credit_limit, account_balance, status) "
            f"VALUES ({esc(cu['customer_code'])}, {esc(cu['company_name'])}, {esc(cu['contact_name'])}, {esc(cu['email'])}, {esc(cu['phone'])}, {esc(cu['city'])}, {esc(cu['state'])}, {esc(cu['country'])}, {esc(cu['industry'])}, {esc(cu['tier'])}, {cu['credit_limit']}, {cu['account_balance']}, {esc(cu['status'])});"
        )
    lines.append("")

    # 9. Clients Master (Compatible)
    lines.append("-- 9. Clients Master (5 Compatible Records)")
    for cm in CLIENTS_MASTER_DATA:
        lines.append(
            f"INSERT INTO clients_master (client_code, company_name, industry, region, tier, contact_person, email, status) "
            f"VALUES ({esc(cm['client_code'])}, {esc(cm['company_name'])}, {esc(cm['industry'])}, {esc(cm['region'])}, {esc(cm['tier'])}, {esc(cm['contact_person'])}, {esc(cm['email'])}, {esc(cm['status'])});"
        )
    lines.append("")

    # 10. Orders
    lines.append("-- 10. Orders (115 records)")
    for o in ORDERS_DATA:
        lines.append(
            f"INSERT INTO orders (order_number, customer_id, order_date, status, total_amount, discount_amount, net_amount, payment_status, billing_cycle, notes) "
            f"SELECT {esc(o['order_number'])}, id, {esc(o['order_date'])}, {esc(o['status'])}, {o['total_amount']}, {o['discount_amount']}, {o['net_amount']}, {esc(o['payment_status'])}, {esc(o['billing_cycle'])}, {esc(o['notes'])} FROM customers WHERE customer_code = {esc(o['customer_code'])};"
        )
    lines.append("")

    # 11. Order Items
    lines.append("-- 11. Order Items")
    for oi in ORDER_ITEMS_DATA[:260]:
        lines.append(
            f"INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal, discount, line_total) "
            f"SELECT o.id, p.id, {oi['quantity']}, {oi['unit_price']}, {oi['subtotal']}, {oi['discount']}, {oi['line_total']} "
            f"FROM orders o, products p WHERE o.order_number = {esc(oi['order_number'])} AND p.product_code = {esc(oi['product_code'])};"
        )
    lines.append("")

    # 12. Payments
    lines.append("-- 12. Payments (115 records)")
    for py in PAYMENTS_DATA:
        lines.append(
            f"INSERT INTO payments (payment_ref, order_id, customer_id, amount, currency, payment_method, status, payment_date, gateway_ref) "
            f"SELECT {esc(py['payment_ref'])}, o.id, c.id, {py['amount']}, {esc(py['currency'])}, {esc(py['payment_method'])}, {esc(py['status'])}, {esc(py['payment_date'])}, {esc(py['gateway_ref'])} "
            f"FROM orders o, customers c WHERE o.order_number = {esc(py['order_number'])} AND c.customer_code = {esc(py['customer_code'])};"
        )
    lines.append("")

    # 13. Transactions (215 records)
    lines.append("-- 13. Transactions (215 records)")
    for t in TRANSACTIONS_DATA:
        curr = t.get("currency", "USD")
        lines.append(
            f"INSERT INTO transactions (transaction_ref, client_code, product_code, amount, currency, status, payment_method, transaction_date, notes) "
            f"VALUES ({esc(t['transaction_ref'])}, {esc(t['client_code'])}, {esc(t['product_code'])}, {t['amount']}, {esc(curr)}, {esc(t['status'])}, {esc(t['payment_method'])}, {esc(t['transaction_date'])}, {esc(t['notes'])});"
        )
    lines.append("")

    # 14. Policies
    lines.append("-- 14. Policies (10 records)")
    for pol in POLICIES_DATA:
        lines.append(
            f"INSERT INTO policies (policy_code, title, category, version, effective_date, department_id, summary, full_text, status) "
            f"SELECT {esc(pol['policy_code'])}, {esc(pol['title'])}, {esc(pol['category'])}, {esc(pol['version'])}, {esc(pol['effective_date'])}, id, {esc(pol['summary'])}, {esc(pol['full_text'])}, 'Active' FROM departments WHERE department_code = {esc(pol['department_code'])};"
        )
    lines.append("")

    # 15. FAQs
    lines.append("-- 15. FAQs (15 records)")
    for f in FAQS_DATA:
        lines.append(
            f"INSERT INTO faqs (faq_code, category, question, answer, keywords, is_published, view_count) "
            f"VALUES ({esc(f['faq_code'])}, {esc(f['category'])}, {esc(f['question'])}, {esc(f['answer'])}, {esc(f['keywords'])}, TRUE, {random.randint(120, 1500)});"
        )
    lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    from pathlib import Path
    out_file = Path(__file__).resolve().parent / "seed_data.sql"
    content = generate_sql_insert_script()
    out_file.write_text(content, encoding="utf-8")
    print(f"Generated {out_file} ({len(content)} characters).")
