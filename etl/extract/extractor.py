import pandas as pd
import os

def extraer_csv1():
    ruta = "/opt/airflow/data/raw/data.csv"
    df = pd.read_csv(ruta, encoding="ISO-8859-1")
    print(f"CSV1 - Registros extraídos: {len(df)}")
    print(f"CSV1 - Columnas: {list(df.columns)}")
    print(f"CSV1 - Nulos por columna:\n{df.isnull().sum()}")
    df.to_csv("/opt/airflow/data/raw/raw_csv1.csv", index=False)
    return len(df)

def extraer_csv2():
    ruta = "/opt/airflow/data/raw/online_retail_II.xlsx"
    if not os.path.exists(ruta):
        print("CSV2 aún no disponible, saltando...")
        return 0
    df = pd.read_excel(ruta, engine="openpyxl")
    print(f"CSV2 - Registros extraídos: {len(df)}")
    print(f"CSV2 - Columnas: {list(df.columns)}")
    print(f"CSV2 - Nulos por columna:\n{df.isnull().sum()}")
    df.to_csv("/opt/airflow/data/raw/raw_csv2.csv", index=False)
    return len(df)
