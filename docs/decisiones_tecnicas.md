# Decisiones Técnicas — DataMart ETL Pipeline

## 1. Modelo del repositorio analítico

Se diseñaron 3 tablas en PostgreSQL:

- **ventas** — contiene todas las transacciones válidas con cantidad > 0 y precio > 0. Incluye revenue_bruto calculado como cantidad × precio_unitario.
- **devoluciones** — contiene transacciones con cantidad <= 0, separadas de las ventas para permitir calcular el neto.
- **log_rechazos** — registra todos los registros que no cumplen las reglas de negocio, con el motivo del rechazo y la fuente de origen.

Esta separación permite calcular el revenue neto como:
```sql
SELECT stock_code, SUM(revenue_bruto) - COALESCE(SUM(dev.total_devuelto), 0) as revenue_neto
FROM ventas v
LEFT JOIN (SELECT stock_code, SUM(quantity * unit_price) as total_devuelto FROM devoluciones GROUP BY stock_code) dev
USING (stock_code)
GROUP BY stock_code;
```

## 2. Casos ambiguos resueltos

### Transacciones sin CustomerID
**Decisión:** Se incluyen en el análisis asignándoles el valor "ANONIMO".
**Justificación:** Excluirlas eliminaría un volumen significativo de transacciones válidas. Al etiquetarlas como "ANONIMO" se pueden incluir en el análisis de ventas y también analizar su comportamiento por separado.

### Descripciones inconsistentes del mismo producto
**Decisión:** Se aplica Title Case a todas las descripciones (primera letra en mayúscula).
**Justificación:** Estandariza todas las variaciones (CANDLE HOLDER WHITE, candle holder white) a un formato único (Candle Holder White) de forma consistente y automatizable.

### Duplicados entre CSV1 y CSV2
**Decisión:** Se eliminan duplicados exactos después de unir ambas fuentes con drop_duplicates().
**Justificación:** Ambas fuentes representan el mismo tipo de transacción. Un registro duplicado exacto (mismo InvoiceNo, StockCode, Quantity, Date) se considera el mismo evento registrado dos veces.

## 3. Idempotencia del DAG

El DAG es idempotente porque antes de cargar los datos ejecuta:
```sql
TRUNCATE TABLE ventas, devoluciones, log_rechazos RESTART IDENTITY
```
Esto garantiza que ejecutar el pipeline dos veces con los mismos datos produce exactamente el mismo resultado.

## 4. Manejo de fechas

Los dos datasets tienen formatos de fecha distintos:
- CSV1: formato americano (12/1/2010 8:26)
- CSV2: formato ISO (2009-12-01 07:45:00)

Se resolvió usando `pd.to_datetime(format="mixed")` que detecta automáticamente el formato de cada registro y los convierte a UTC.

## 5. Normalización de StockCode

Todos los códigos de producto se convierten a mayúsculas y se eliminan espacios con `.str.upper().str.strip()` para garantizar consistencia al cruzarlos con el catálogo.


## 6.Diagrama del modelo de datos

[Ver diagrama en dbdiagram.io] https://dbdiagram.io/d/6a3b0f80d0074fe75d0b4f50