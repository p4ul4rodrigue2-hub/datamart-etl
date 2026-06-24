CREATE TABLE IF NOT EXISTS ventas (
    id SERIAL PRIMARY KEY,
    invoice_no VARCHAR(20),
    stock_code VARCHAR(20),
    description VARCHAR(255),
    quantity INT,
    invoice_date TIMESTAMPTZ,
    unit_price DECIMAL(10,2),
    customer_id VARCHAR(20),
    country VARCHAR(100),
    revenue_bruto DECIMAL(10,2),
    revenue_neto DECIMAL(10,2),
    fuente VARCHAR(10)
);

CREATE TABLE IF NOT EXISTS devoluciones (
    id SERIAL PRIMARY KEY,
    invoice_no VARCHAR(20),
    stock_code VARCHAR(20),
    description VARCHAR(255),
    quantity INT,
    invoice_date TIMESTAMPTZ,
    unit_price DECIMAL(10,2),
    customer_id VARCHAR(20),
    country VARCHAR(100),
    fuente VARCHAR(10)
);

CREATE TABLE IF NOT EXISTS log_rechazos (
    id SERIAL PRIMARY KEY,
    invoice_no VARCHAR(20),
    stock_code VARCHAR(20),
    description VARCHAR(255),
    quantity INT,
    invoice_date VARCHAR(50),
    unit_price DECIMAL(10,2),
    customer_id VARCHAR(20),
    country VARCHAR(100),
    motivo VARCHAR(255),
    fuente VARCHAR(10)
);
