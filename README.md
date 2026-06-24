# DataMart ETL Pipeline

Pipeline ETL construido con Apache Airflow 2.9.1 en Docker. Procesa datos de transacciones de e-commerce desde dos fuentes heterogéneas, los transforma y los carga en un repositorio analítico PostgreSQL.

## Contexto del negocio

DataMart S.A.S. es una empresa colombiana de comercio electrónico que opera en Colombia, México y Perú. Durante 2023 experimentó un crecimiento del 40% en transacciones, pero sus datos de ventas están dispersos en archivos planos sin estructura analítica.

Este pipeline ETL es la primera pieza de su plataforma de datos. Consolida transacciones de dos fuentes históricas, aplica reglas de calidad y las deja disponibles en un repositorio analítico PostgreSQL para que el equipo de negocio pueda consultarlas.

**Fuentes de datos:**
- `data.csv` — transacciones diarias de la tienda en línea
- `online_retail_II.xlsx` — historial extendido de dos años adicionales

**Repositorio analítico:**
- `ventas` — transacciones válidas con revenue bruto y neto
- `devoluciones` — transacciones con cantidad negativa
- `log_rechazos` — registros que no cumplen reglas de negocio

---

## Arquitectura
data.csv + online_retail_II.xlsx

↓ Extract → data/raw/

↓ Transform → data/processed/

↓ Load

paula_r (PostgreSQL analítico)

---

## Servicios Docker

| Servicio | Descripción | Puerto |
|---|---|---|
| `postgres` | Metadatos internos de Airflow | 5432 |
| `analytics_db` | Repositorio analítico destino | 5433 |
| `airflow-webserver` | UI de Airflow | 8080 |
| `airflow-scheduler` | Orquestador de DAGs | — |

---

## Requisitos

- Docker y Docker Compose
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

> Las credenciales reales nunca se suben al repositorio. El `.env` está excluido en `.gitignore`.

### 3 — Agregar los archivos de datos

Descarga los archivos desde Kaggle y cópialos en `data/raw/`:

- [data.csv](https://www.kaggle.com/datasets/carrie1/ecommerce-data)
- [online_retail_II.xlsx](https://www.kaggle.com/datasets/thedevastator/online-retail-transaction-dataset)
data/raw/data.csv

data/raw/online_retail_II.xlsx

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

Espera a ver `exited with code 0`. Este comando crea automáticamente:
- Usuario admin
- Airflow Connection `analytics_db`
- Variables `batch_size` y `fuentes_activas`

### 6 — Levantar todos los servicios

```bash
sudo docker compose up -d
```

> Las dependencias Python (pandas, psycopg2, openpyxl) se instalan automáticamente mediante el Dockerfile al construir la imagen.

### 7 — Ejecutar el pipeline

1. Abre `http://localhost:8080`
2. Usuario: `admin` / Contraseña: `admin`
3. Activa el DAG `datamart_etl`
4. Haz clic en ▶ para ejecutarlo

---

## Verificar que los datos llegaron

```bash
PGPASSWORD='<contraseña>' psql -h <host> -p <puerto> -U <usuario> -d <nombre_db>
```

```sql
SELECT COUNT(*) FROM ventas;
SELECT COUNT(*) FROM devoluciones;
SELECT COUNT(*) FROM log_rechazos;
```

---

## Validar Connections y Variables en Airflow

### Connections
1. Ve a **Admin → Connections**
2. Verifica que existe `analytics_db`

### Variables
1. Ve a **Admin → Variables**
2. Verifica que existen `batch_size` y `fuentes_activas`

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

│   ├── ddl.sql

│   └── consultas_negocio.sql

├── Dockerfile

├── docker-compose.yml

├── .env.example

├── .gitignore

└── README.md

---

## Diagrama del modelo de datos

[Ver diagrama en dbdiagram.io](https://dbdiagram.io/d/6a3b0f80d0074fe75d0b4f50)

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

Download from Kaggle and copy to `data/raw/`:

- [data.csv](https://www.kaggle.com/datasets/carrie1/ecommerce-data)
- [online_retail_II.xlsx](https://www.kaggle.com/datasets/thedevastator/online-retail-transaction-dataset)

### 4 — Set permissions

```bash
sudo chown -R 50000:0 logs dags plugins etl data
sudo chmod -R 777 logs dags plugins etl data
```

### 5 — Initialize Airflow

```bash
sudo docker compose up airflow-init
```

This automatically creates the admin user, `analytics_db` Connection, and Airflow Variables.

### 6 — Start all services

```bash
sudo docker compose up -d
```

> Python dependencies are installed automatically via Dockerfile.

### 7 — Run the pipeline

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

## Diagram

[View on dbdiagram.io](https://dbdiagram.io/d/6a3b0f80d0074fe75d0b4f50)