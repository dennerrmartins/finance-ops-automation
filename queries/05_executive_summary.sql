-- =============================================================================
-- 05 — Sumário Executivo
-- =============================================================================

-- 5.1: KPIs gerais do pipeline
SELECT
    (SELECT COUNT(*) FROM invoices WHERE status = 'sucesso') AS notas_processadas,
    (SELECT COUNT(DISTINCT supplier_id) FROM invoices) AS fornecedores_ativos,
    (SELECT ROUND(SUM(amount), 2) FROM invoices) AS gasto_total,
    (SELECT COUNT(*) FROM payment_tickets WHERE status = 'pago') AS tickets_pagos;

-- 5.2: Ranking de áreas por eficiência orçamentária (menor estouro primeiro)
WITH resumo AS (
    SELECT
        b.area,
        SUM(b.budget_amount) AS orcado,
        COALESCE(SUM(a.amount), 0) AS realizado
    FROM budget_lines b
    LEFT JOIN actuals a ON a.budget_line_id = b.id
    GROUP BY b.area
)
SELECT
    area,
    ROUND(orcado, 2) AS orcado_total,
    ROUND(realizado, 2) AS realizado_total,
    ROUND(100.0 * realizado / orcado, 2) AS pct_consumido
FROM resumo
ORDER BY pct_consumido;

-- 5.3: CTE — visão consolidada CMEF
WITH gastos AS (
    SELECT
        s.area,
        i.issue_month AS month,
        SUM(i.amount) AS realizado
    FROM invoices i
    JOIN suppliers s ON s.id = i.supplier_id
    GROUP BY s.area, i.issue_month
)
SELECT
    b.area,
    b.month,
    ROUND(b.budget_amount, 2) AS orcado,
    ROUND(COALESCE(g.realizado, 0), 2) AS realizado,
    CASE
        WHEN COALESCE(g.realizado, 0) > b.budget_amount THEN 'ACIMA'
        WHEN COALESCE(g.realizado, 0) < b.budget_amount * 0.9 THEN 'ABAIXO'
        ELSE 'OK'
    END AS status_linha
FROM budget_lines b
LEFT JOIN gastos g ON g.area = b.area AND g.month = b.month
ORDER BY b.month, b.area;

-- 5.4: Ponte operacional → DRE — fornecedor mapeado à linha CMEF
SELECT
    s.name AS fornecedor,
    a.account_name AS linha_dre_cmef,
    ROUND(SUM(i.amount), 2) AS real_operacional_nf
FROM invoices i
JOIN suppliers s ON s.id = i.supplier_id
JOIN dre_accounts a ON a.account_code = s.dre_account_code
GROUP BY s.id, a.account_name
ORDER BY real_operacional_nf DESC;
