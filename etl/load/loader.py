import pandas as pd
from psycopg2.extras import execute_values
from airflow.hooks.postgres_hook import PostgresHook
import os

def get_conn():
    try:
        hook = PostgresHook(postgres_conn_id="analytics_db")
        return hook.get_conn()
    except Exception:
        import psycopg2
        return psycopg2.connect(
            host=os.getenv("ANALYTICS_DB_HOST", "15.204.173.204"),
            port=os.getenv("ANALYTICS_DB_PORT", "6432"),
            dbname=os.getenv("ANALYTICS_DB_NAME", "paula_r"),
            user=os.getenv("ANALYTICS_DB_USER", "coder-ra-c6"),
            password=os.getenv("ANALYTICS_DB_PASSWORD", "Riwi2026**"),
        )

def crear_tablas():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
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
        )
    """)
    cursor.execute("""
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
        )
    """)
    cursor.execute("""
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
        )
    """)
    conn.commit()
    conn.close()
    print("Tablas creadas correctamente")

def cargar():
    from airflow.models import Variable
    batch_size = int(Variable.get("batch_size", default_var=5000))

    crear_tablas()
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("TRUNCATE TABLE ventas, devoluciones, log_rechazos RESTART IDENTITY")
    conn.commit()

    ventas = pd.read_csv("/opt/airflow/data/processed/ventas.csv")
    ventas = ventas.fillna("")
    datos_ventas = [
        (row["InvoiceNo"], row["StockCode"], row["Description"], row["Quantity"],
         row["InvoiceDate"], row["UnitPrice"], row["CustomerID"], row["Country"],
         row["revenue_bruto"], row["revenue_neto"], row["fuente"])
        for _, row in ventas.iterrows()
    ]
    execute_values(cursor, """
        INSERT INTO ventas (invoice_no, stock_code, description, quantity,
            invoice_date, unit_price, customer_id, country, revenue_bruto, revenue_neto, fuente)
        VALUES %s
    """, datos_ventas, page_size=batch_size)
    print(f"Ventas cargadas: {len(datos_ventas)}")

    devoluciones = pd.read_csv("/opt/airflow/data/processed/devoluciones.csv")
    devoluciones = devoluciones.fillna("")
    datos_dev = [
        (row["InvoiceNo"], row["StockCode"], row["Description"], row["Quantity"],
         row["InvoiceDate"], row["UnitPrice"], row["CustomerID"], row["Country"],
         row["fuente"])
        for _, row in devoluciones.iterrows()
    ]
    execute_values(cursor, """
        INSERT INTO devoluciones (invoice_no, stock_code, description, quantity,
            invoice_date, unit_price, customer_id, country, fuente)
        VALUES %s
    """, datos_dev, page_size=batch_size)
    print(f"Devoluciones cargadas: {len(datos_dev)}")

    rechazos = pd.read_csv("/opt/airflow/data/processed/rechazos.csv")
    rechazos = rechazos.fillna("")
    datos_rechazos = [
        (row["InvoiceNo"], row["StockCode"], row["Description"], row["Quantity"],
         row["InvoiceDate"], row["UnitPrice"], row["CustomerID"], row["Country"],
         row["motivo"], row["fuente"])
        for _, row in rechazos.iterrows()
    ]
    execute_values(cursor, """
        INSERT INTO log_rechazos (invoice_no, stock_code, description, quantity,
            invoice_date, unit_price, customer_id, country, motivo, fuente)
        VALUES %s
    """, datos_rechazos, page_size=batch_size)
    print(f"Rechazos cargados: {len(datos_rechazos)}")

    conn.commit()
    conn.close()
    print("Datos cargados correctamente")
