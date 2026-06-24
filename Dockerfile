FROM apache/airflow:2.9.1
RUN pip install pandas psycopg2-binary openpyxl
