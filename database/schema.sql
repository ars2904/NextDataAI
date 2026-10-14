-- ============================================================================
-- NexaData AI Enterprise Database Schema (PostgreSQL)
-- Supports relational Q&A for Company Info, Departments, Employees, Policies,
-- FAQs, Customers, Products, Categories, Suppliers, Orders, Order Items,
-- Payments, Transactions, and Inventory.
-- ============================================================================

-- 1. Company Information
CREATE TABLE IF NOT EXISTS company_info (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(150) NOT NULL,
    legal_name VARCHAR(150) NOT NULL,
    tagline VARCHAR(255) NOT NULL,
    tax_id VARCHAR(50),
    founded_year INT NOT NULL,
    headquarters VARCHAR(255) NOT NULL,
    website VARCHAR(120) NOT NULL,
    support_email VARCHAR(120) NOT NULL,
    sales_email VARCHAR(120) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    mission TEXT NOT NULL,
    vision TEXT NOT NULL,
    fiscal_year_end VARCHAR(30) DEFAULT 'December 31',
    primary_currency VARCHAR(10) DEFAULT 'USD',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Departments
CREATE TABLE IF NOT EXISTS departments (
    id SERIAL PRIMARY KEY,
    department_code VARCHAR(30) UNIQUE NOT NULL,
    name VARCHAR(120) NOT NULL,
    head_of_department VARCHAR(120) NOT NULL,
    budget NUMERIC(14, 2) NOT NULL,
    location VARCHAR(120) NOT NULL,
    employee_count INT DEFAULT 0,
    contact_email VARCHAR(120) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Employees
CREATE TABLE IF NOT EXISTS employees (
    id SERIAL PRIMARY KEY,
    employee_code VARCHAR(30) UNIQUE NOT NULL,
    first_name VARCHAR(60) NOT NULL,
    last_name VARCHAR(60) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    phone VARCHAR(30),
    department_id INT REFERENCES departments(id) ON DELETE SET NULL,
    role VARCHAR(120) NOT NULL,
    salary NUMERIC(12, 2) NOT NULL,
    hire_date DATE NOT NULL,
    status VARCHAR(30) DEFAULT 'Active',
    location VARCHAR(120) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Product Categories
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    category_code VARCHAR(30) UNIQUE NOT NULL,
    name VARCHAR(120) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Suppliers & Infrastructure Vendors
CREATE TABLE IF NOT EXISTS suppliers (
    id SERIAL PRIMARY KEY,
    supplier_code VARCHAR(30) UNIQUE NOT NULL,
    name VARCHAR(150) NOT NULL,
    contact_name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL,
    phone VARCHAR(30),
    country VARCHAR(60) NOT NULL,
    service_type VARCHAR(120) NOT NULL,
    rating NUMERIC(3, 2) DEFAULT 5.0,
    payment_terms VARCHAR(50) DEFAULT 'Net 30',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. Products (Compatible with existing NexaData product catalog)
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    product_code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(150) NOT NULL,
    tier VARCHAR(50) NOT NULL,
    category_id INT REFERENCES categories(id) ON DELETE SET NULL,
    supplier_id INT REFERENCES suppliers(id) ON DELETE SET NULL,
    price NUMERIC(12, 2) NOT NULL,
    cost_price NUMERIC(12, 2) DEFAULT 0.0,
    billing_type VARCHAR(50) NOT NULL,
    stock_quantity INT DEFAULT 100,
    description TEXT NOT NULL,
    features TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 7. Inventory Records
CREATE TABLE IF NOT EXISTS inventory (
    id SERIAL PRIMARY KEY,
    product_id INT REFERENCES products(id) ON DELETE CASCADE,
    sku VARCHAR(60) UNIQUE NOT NULL,
    warehouse_location VARCHAR(120) NOT NULL,
    quantity_available INT NOT NULL DEFAULT 0,
    quantity_reserved INT NOT NULL DEFAULT 0,
    reorder_level INT NOT NULL DEFAULT 10,
    unit_cost NUMERIC(12, 2) NOT NULL,
    last_restocked DATE,
    status VARCHAR(40) DEFAULT 'In Stock',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 8. Customer Accounts (Supports 50+ Customers)
CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    customer_code VARCHAR(50) UNIQUE NOT NULL,
    company_name VARCHAR(150) NOT NULL,
    contact_name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL,
    phone VARCHAR(40),
    city VARCHAR(80) NOT NULL,
    state VARCHAR(80),
    country VARCHAR(80) NOT NULL,
    industry VARCHAR(100) NOT NULL,
    tier VARCHAR(50) DEFAULT 'Standard',
    credit_limit NUMERIC(14, 2) DEFAULT 50000.00,
    account_balance NUMERIC(14, 2) DEFAULT 0.00,
    sales_rep_id INT REFERENCES employees(id) ON DELETE SET NULL,
    status VARCHAR(40) DEFAULT 'Active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 9. Existing Compatible Client Master Accounts (Preserved for backwards compatibility)
CREATE TABLE IF NOT EXISTS clients_master (
    id SERIAL PRIMARY KEY,
    client_code VARCHAR(50) UNIQUE NOT NULL,
    company_name VARCHAR(150) NOT NULL,
    industry VARCHAR(100) NOT NULL,
    region VARCHAR(100) NOT NULL,
    tier VARCHAR(50) NOT NULL,
    contact_person VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL,
    status VARCHAR(50) DEFAULT 'Active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 10. Orders (Supports 100+ Orders)
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    order_number VARCHAR(60) UNIQUE NOT NULL,
    customer_id INT REFERENCES customers(id) ON DELETE RESTRICT,
    order_date DATE NOT NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'Completed',
    total_amount NUMERIC(14, 2) NOT NULL,
    discount_amount NUMERIC(14, 2) DEFAULT 0.00,
    net_amount NUMERIC(14, 2) NOT NULL,
    payment_status VARCHAR(40) NOT NULL DEFAULT 'Paid',
    sales_rep_id INT REFERENCES employees(id) ON DELETE SET NULL,
    billing_cycle VARCHAR(40) DEFAULT 'Monthly',
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 11. Order Line Items
CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(id) ON DELETE CASCADE,
    product_id INT REFERENCES products(id) ON DELETE RESTRICT,
    quantity INT NOT NULL DEFAULT 1,
    unit_price NUMERIC(12, 2) NOT NULL,
    subtotal NUMERIC(12, 2) NOT NULL,
    discount NUMERIC(12, 2) DEFAULT 0.00,
    line_total NUMERIC(12, 2) NOT NULL
);

-- 12. Payments
CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    payment_ref VARCHAR(60) UNIQUE NOT NULL,
    order_id INT REFERENCES orders(id) ON DELETE CASCADE,
    customer_id INT REFERENCES customers(id) ON DELETE RESTRICT,
    amount NUMERIC(14, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    payment_method VARCHAR(50) NOT NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'Success',
    payment_date DATE NOT NULL,
    gateway_ref VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 13. Sales & Subscription Transactions (Preserves & Expands to 200+ Transactions)
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    transaction_ref VARCHAR(60) UNIQUE NOT NULL,
    client_code VARCHAR(50) NOT NULL,
    product_code VARCHAR(50) NOT NULL,
    amount NUMERIC(14, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    status VARCHAR(50) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    transaction_date VARCHAR(40) NOT NULL,
    notes TEXT,
    customer_id INT REFERENCES customers(id) ON DELETE SET NULL,
    order_id INT REFERENCES orders(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 14. Company Policies
CREATE TABLE IF NOT EXISTS policies (
    id SERIAL PRIMARY KEY,
    policy_code VARCHAR(40) UNIQUE NOT NULL,
    title VARCHAR(160) NOT NULL,
    category VARCHAR(60) NOT NULL,
    version VARCHAR(20) DEFAULT 'v1.0',
    effective_date DATE NOT NULL,
    department_id INT REFERENCES departments(id) ON DELETE SET NULL,
    summary TEXT NOT NULL,
    full_text TEXT NOT NULL,
    status VARCHAR(30) DEFAULT 'Active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 15. Corporate FAQs
CREATE TABLE IF NOT EXISTS faqs (
    id SERIAL PRIMARY KEY,
    faq_code VARCHAR(40) UNIQUE NOT NULL,
    category VARCHAR(60) NOT NULL,
    question VARCHAR(255) NOT NULL,
    answer TEXT NOT NULL,
    keywords VARCHAR(255),
    is_published BOOLEAN DEFAULT TRUE,
    view_count INT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for optimal lookup performance
CREATE INDEX IF NOT EXISTS idx_products_code ON products(product_code);
CREATE INDEX IF NOT EXISTS idx_customers_code ON customers(customer_code);
CREATE INDEX IF NOT EXISTS idx_orders_number ON orders(order_number);
CREATE INDEX IF NOT EXISTS idx_transactions_ref ON transactions(transaction_ref);
CREATE INDEX IF NOT EXISTS idx_transactions_client ON transactions(client_code);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_inventory_product ON inventory(product_id);
CREATE INDEX IF NOT EXISTS idx_policies_code ON policies(policy_code);
CREATE INDEX IF NOT EXISTS idx_faqs_category ON faqs(category);
