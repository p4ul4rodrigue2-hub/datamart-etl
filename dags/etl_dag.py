from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import sys

sys.path.insert(0, '/opt/airflow')

from etl.extract.extractor import extraer_csv1, extraer_csv2
from etl.transform.transformer import transformar
from etl.load.loader import cargar

with DAG(
    dag_id="datamart_etl",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
) as dag:

    t1 = PythonOperator(task_id="extraer_csv1", python_callable=extraer_csv1, retries=2)
    t2 = PythonOperator(task_id="extraer_csv2", python_callable=extraer_csv2, retries=2)
    t3 = PythonOperator(task_id="transformar", python_callable=transformar, retries=2)
    t4 = PythonOperator(task_id="cargar", python_callable=cargar, retries=2)

    [t1, t2] >> t3 >> t4
