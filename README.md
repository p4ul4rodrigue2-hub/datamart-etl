## DATAMART 



Pipeline ETL construido con Apache Airflow 2.9.1 en Docker. Procesa datos de transacciones de e-commerce desde dos fuentes heterogéneas, los transforma y los carga en un repositorio analítico PostgreSQL.

---

## Arquitectura
data.csv + online_retail_II.xlsx

↓ Extract

data/raw/

↓ Transform

data/processed/

↓ Load

paula_r (PostgreSQL analítico)

## Servicios Docker

| Servicio | Descripción | Puerto |
|---|---|---|
| `postgres` | Metadatos internos de Airflow | 5432 |
| `analytics_db` | Repositorio analítico destino | 5433 |
| `airflow-webserver` | UI de Airflow | 8080 |
| `airflow-scheduler` | Orquestador de DAGs | — |

---

## Requisitos

- Docker
- Docker Compose
- Linux / Ubuntu

---

## Instalación

### 1 — Clonar el repositorio

```bash
git clone https://github.com/p4ul4rodrigue2-hub/datamart-etl.git
cd datamart-etl
```

### 2 — Configurar variables de entorno

```bash
cp .env.example .env
```

Edita el `.env` con tus credenciales:
AIRFLOW_UID=1001

ANALYTICS_DB_HOST=<host>

ANALYTICS_DB_PORT=<puerto>

ANALYTICS_DB_NAME=<nombre_db>

ANALYTICS_DB_USER=<usuario>

ANALYTICS_DB_PASSWORD=<contraseña>

### 3 — Agregar los archivos de datos

Descarga los archivos desde Kaggle y cópialos en la carpeta `data/raw/`:

- [data.csv] https://www.kaggle.com/datasets/carrie1/ecommerce-data
- [online_retail_II.xlsx] https://www.kaggle.com/datasets/thedevastator/online-retail-transaction-dataset

```
data/raw/data.csv
data/raw/online_retail_II.xlsx
```
### 4 — Crear carpetas y permisos

```bash
mkdir -p dags logs plugins etl/extract etl/transform etl/load data/raw data/processed
sudo chown -R 50000:0 logs dags plugins etl data
sudo chmod -R 777 logs dags plugins etl data
```

### 5 — Inicializar Airflow

```bash
sudo docker compose up airflow-init
```

Espera a ver `exited with code 0`.

### 6 — Levantar todos los servicios

```bash
sudo docker compose up -d
```

### 7 — Instalar dependencias

```bash
sudo docker exec -it --user airflow datamart-etl-airflow-scheduler-1 python -m pip install pandas psycopg2-binary openpyxl
sudo docker exec -it --user airflow datamart-etl-airflow-webserver-1 python -m pip install pandas psycopg2-binary openpyxl
```

### 8 — Ejecutar el pipeline

1. Abre `http://localhost:8080`
2. Usuario: `admin` / Contraseña: `admin`
3. Activa el DAG `datamart_etl`
4. Haz clic en ▶ para ejecutarlo

---

## Verificar que los datos llegaron

Conéctate al repositorio analítico:

```bash
psql -h <ANALYTICS_DB_HOST> -p <ANALYTICS_DB_PORT> -U <ANALYTICS_DB_USER> -d <ANALYTICS_DB_NAME> -W
```

Ejecuta:

```sql
SELECT COUNT(*) FROM ventas;
SELECT COUNT(*) FROM devoluciones;
SELECT COUNT(*) FROM log_rechazos;
```

---

## Validar Connections y Variables en Airflow

### Connections
1. Ve a **Admin → Connections**
2. Verifica que existe `analytics_db` con el host y credenciales correctas

### Variables
1. Ve a **Admin → Variables**
2. Verifica que existen:
   - `batch_size`
   - `fuentes_activas`

---

## Estructura del proyecto
datamart-etl/

├── dags/

│   └── etl_dag.py

├── etl/

│   ├── extract/extractor.py

│   ├── transform/transformer.py

│   └── load/loader.py

├── data/

│   └── raw/

├── docs/

│   └── decisiones_tecnicas.md

├── sql/

│   └── consultas_negocio.sql

├── docker-compose.yml

├── .env.example

├── .gitignore

└── README.md

---

## Tecnologías

- Apache Airflow 2.9.1
- PostgreSQL 13
- Python 3.12
- pandas, psycopg2, openpyxl
- Docker / Docker Compose

---

# English Version

## DataMart ETL Pipeline

ETL pipeline built with Apache Airflow 2.9.1 on Docker. Processes e-commerce transaction data from two heterogeneous sources, transforms it, and loads it into a PostgreSQL analytical repository.

## Quick Start

### 1 — Clone the repository

```bash
git clone https://github.com/p4ul4rodrigue2-hub/datamart-etl.git
cd datamart-etl
```

### 2 — Set up environment variables

```bash
cp .env.example .env
```

Edit `.env` with your credentials.

### 3 — Add data files

Copy CSV/XLSX files to `data/raw/`:
data/raw/data.csv

data/raw/online_retail_II.xlsx

### 4 — Set permissions

```bash
sudo chown -R 50000:0 logs dags plugins etl data
sudo chmod -R 777 logs dags plugins etl data
```

### 5 — Initialize Airflow

```bash
sudo docker compose up airflow-init
```

### 6 — Start all services

```bash
sudo docker compose up -d
```

### 7 — Install dependencies

```bash
sudo docker exec -it --user airflow datamart-etl-airflow-scheduler-1 python -m pip install pandas psycopg2-binary openpyxl
sudo docker exec -it --user airflow datamart-etl-airflow-webserver-1 python -m pip install pandas psycopg2-binary openpyxl
```

### 8 — Run the pipeline

1. Open `http://localhost:8080`
2. User: `admin` / Password: `admin`
3. Enable DAG `datamart_etl`
4. Click ▶ to trigger

## Verify data loaded

```sql
SELECT COUNT(*) FROM ventas;
SELECT COUNT(*) FROM devoluciones;
SELECT COUNT(*) FROM log_rechazos;
```
EOF


## Diagrama del modelo de datos

[Ver diagrama en dbdiagram.io] https://dbdiagram.io/d/6a3b0f80d0074fe75d0b4f50