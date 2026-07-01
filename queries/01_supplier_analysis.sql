-- =============================================================================
-- 01 — Análise de Fornecedores
-- =============================================================================

-- 1.1: Top fornecedores por valor total pago
SELECT
    s.name AS fornecedor,
    s.area,
    COUNT(i.id) AS qtd_notas,
    ROUND(SUM(i.amount), 2) AS valor_total
FROM invoices i
JOIN suppliers s ON s.id = i.supplier_id
WHERE i.status = 'sucesso'
GROUP BY s.id
ORDER BY valor_total DESC;

-- 1.2: Concentração de gastos por área
SELECT
    s.area,
    COUNT(DISTINCT s.id) AS fornecedores,
    ROUND(SUM(i.amount), 2) AS gasto_total,
    ROUND(100.0 * SUM(i.amount) / (SELECT SUM(amount) FROM invoices), 2) AS pct_do_total
FROM invoices i
JOIN suppliers s ON s.id = i.supplier_id
GROUP BY s.area
ORDER BY gasto_total DESC;

-- 1.3: Ticket médio por fornecedor
SELECT
    s.name AS fornecedor,
    ROUND(AVG(i.amount), 2) AS ticket_medio,
    MIN(i.amount) AS menor_nf,
    MAX(i.amount) AS maior_nf
FROM invoices i
JOIN suppliers s ON s.id = i.supplier_id
GROUP BY s.id
HAVING COUNT(i.id) >= 2
ORDER BY ticket_medio DESC;
