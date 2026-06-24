-- 1. Evolución mensual de ventas netas (descontando devoluciones)
SELECT 
    DATE_TRUNC('month', v.invoice_date) AS mes,
    SUM(v.revenue_bruto) AS ventas_brutas,
    COALESCE(SUM(d.revenue_devuelto), 0) AS devoluciones,
    SUM(v.revenue_bruto) - COALESCE(SUM(d.revenue_devuelto), 0) AS ventas_netas
FROM ventas v
LEFT JOIN (
    SELECT 
        DATE_TRUNC('month', invoice_date) AS mes,
        SUM(ABS(quantity * unit_price)) AS revenue_devuelto
    FROM devoluciones
    GROUP BY 1
) d ON DATE_TRUNC('month', v.invoice_date) = d.mes
GROUP BY 1
ORDER BY 1;

-- 2. Revenue bruto por categoría y proporción de devoluciones
SELECT 
    v.country,
    SUM(v.revenue_bruto) AS revenue_bruto,
    COUNT(d.id) AS total_devoluciones,
    ROUND(COUNT(d.id)::decimal / COUNT(v.id) * 100, 2) AS pct_devoluciones
FROM ventas v
LEFT JOIN devoluciones d ON v.stock_code = d.stock_code
GROUP BY 1
ORDER BY 2 DESC;

-- 3. Top 10 productos con mayor revenue neto
SELECT 
    stock_code,
    description,
    SUM(revenue_bruto) AS revenue_neto
FROM ventas
GROUP BY stock_code, description
ORDER BY revenue_neto DESC
LIMIT 10;

-- 4. Países con mayor concentración de transacciones y ticket promedio
SELECT 
    country,
    COUNT(*) AS total_transacciones,
    ROUND(AVG(revenue_bruto), 2) AS ticket_promedio,
    SUM(revenue_bruto) AS revenue_total
FROM ventas
GROUP BY country
ORDER BY total_transacciones DESC;

-- 5. Comportamiento clientes identificados vs anonimos
SELECT 
    CASE WHEN customer_id = 'ANONIMO' THEN 'Anonimo' ELSE 'Identificado' END AS tipo_cliente,
    COUNT(*) AS total_transacciones,
    ROUND(AVG(revenue_bruto), 2) AS ticket_promedio,
    SUM(revenue_bruto) AS revenue_total
FROM ventas
GROUP BY 1;

-- 6. Productos sin descripción consistente y total códigos únicos
SELECT COUNT(DISTINCT stock_code) AS total_codigos_unicos FROM ventas;

SELECT stock_code, COUNT(DISTINCT description) AS variaciones_descripcion
FROM ventas
GROUP BY stock_code
HAVING COUNT(DISTINCT description) > 1
ORDER BY variaciones_descripcion DESC
LIMIT 20;

-- 7. Recomendación al equipo de producto
SELECT 
    stock_code,
    description,
    SUM(revenue_bruto) AS revenue_bruto,
    COUNT(*) AS total_ventas,
    ROUND(AVG(unit_price), 2) AS precio_promedio
FROM ventas
GROUP BY stock_code, description
ORDER BY revenue_bruto DESC
LIMIT 10;
