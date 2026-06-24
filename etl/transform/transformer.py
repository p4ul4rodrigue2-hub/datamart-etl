import pandas as pd
import os

def transformar():
    df1 = pd.read_csv("/opt/airflow/data/raw/raw_csv1.csv", encoding="ISO-8859-1")
    df1["fuente"] = "csv1"

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

    df["StockCode"] = df["StockCode"].astype(str).str.upper().str.strip()
    df["Description"] = df["Description"].astype(str).str.strip().str.title()
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], format="mixed", dayfirst=False, utc=True)

    devoluciones = df[df["Quantity"] <= 0].copy()
    ventas = df[df["Quantity"] > 0].copy()

    log_rechazos = ventas[ventas["UnitPrice"] <= 0].copy()
    log_rechazos["motivo"] = "UnitPrice <= 0"
    ventas = ventas[ventas["UnitPrice"] > 0]

    ventas["revenue_bruto"] = ventas["Quantity"] * ventas["UnitPrice"]

    ventas["fecha"] = ventas["InvoiceDate"].dt.date
    devoluciones["fecha"] = devoluciones["InvoiceDate"].dt.date
    devoluciones["revenue_devuelto"] = devoluciones["Quantity"].abs() * devoluciones["UnitPrice"]

    neto_por_producto = devoluciones.groupby(["StockCode", "fecha"])["revenue_devuelto"].sum().reset_index()
    neto_por_producto.columns = ["StockCode", "fecha", "total_devuelto"]

    ventas = ventas.merge(neto_por_producto, on=["StockCode", "fecha"], how="left")
    ventas["total_devuelto"] = ventas["total_devuelto"].fillna(0)
    ventas["revenue_neto"] = ventas["revenue_bruto"] - ventas["total_devuelto"]
    ventas = ventas.drop(columns=["total_devuelto", "fecha"])

    ventas["CustomerID"] = ventas["CustomerID"].fillna("ANONIMO").astype(str)
    devoluciones["CustomerID"] = devoluciones["CustomerID"].fillna("ANONIMO").astype(str)

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
