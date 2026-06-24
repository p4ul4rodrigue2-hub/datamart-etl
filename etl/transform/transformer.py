import pandas as pd
import os

def transformar():
    # Cargar CSV1
    df1 = pd.read_csv("/opt/airflow/data/raw/raw_csv1.csv", encoding="ISO-8859-1")
    df1["fuente"] = "csv1"

    # Cargar CSV2 si existe
    ruta_csv2 = "/opt/airflow/data/raw/raw_csv2.csv"
    if os.path.exists(ruta_csv2):
        df2 = pd.read_csv(ruta_csv2, encoding="ISO-8859-1")
        df2 = df2.rename(columns={
            "Invoice": "InvoiceNo",
            "StockCode": "StockCode",
            "Description": "Description",
            "Quantity": "Quantity",
            "InvoiceDate": "InvoiceDate",
            "Price": "UnitPrice",
            "Customer ID": "CustomerID",
            "Country": "Country"
        })
        df2["fuente"] = "csv2"
        df = pd.concat([df1, df2], ignore_index=True)
    else:
        df = df1

    print(f"Total registros antes de limpiar: {len(df)}")

    # 1 - Normalizar StockCode
    df["StockCode"] = df["StockCode"].astype(str).str.upper().str.strip()

    # 2 - Normalizar Description
    df["Description"] = df["Description"].astype(str).str.strip().str.title()

    # 3 - Estandarizar fecha a datetime UTC con formato mixto
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], format="mixed", dayfirst=False, utc=True)

    # 4 - Separar devoluciones
    devoluciones = df[df["Quantity"] <= 0].copy()
    ventas = df[df["Quantity"] > 0].copy()

    # 5 - Rechazar precio unitario <= 0
    log_rechazos = ventas[ventas["UnitPrice"] <= 0].copy()
    log_rechazos["motivo"] = "UnitPrice <= 0"
    ventas = ventas[ventas["UnitPrice"] > 0]

    # 6 - Calcular revenue bruto
    ventas["revenue_bruto"] = ventas["Quantity"] * ventas["UnitPrice"]

    # 7 - Manejar CustomerID nulo
    ventas["CustomerID"] = ventas["CustomerID"].fillna("ANONIMO").astype(str)
    devoluciones["CustomerID"] = devoluciones["CustomerID"].fillna("ANONIMO").astype(str)

    # 8 - Eliminar duplicados
    ventas = ventas.drop_duplicates()
    devoluciones = devoluciones.drop_duplicates()

    print(f"Ventas limpias: {len(ventas)}")
    print(f"Devoluciones: {len(devoluciones)}")
    print(f"Rechazos: {len(log_rechazos)}")

    os.makedirs("/opt/airflow/data/processed", exist_ok=True)
    ventas.to_csv("/opt/airflow/data/processed/ventas.csv", index=False)
    devoluciones.to_csv("/opt/airflow/data/processed/devoluciones.csv", index=False)
    log_rechazos.to_csv("/opt/airflow/data/processed/rechazos.csv", index=False)

    return {"ventas": len(ventas), "devoluciones": len(devoluciones), "rechazos": len(log_rechazos)}
