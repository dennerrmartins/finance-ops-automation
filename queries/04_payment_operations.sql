-- =============================================================================
-- 04 — Operações de Pagamento
-- =============================================================================

-- 4.1: Status dos tickets de pagamento
SELECT
    pt.status,
    COUNT(*) AS quantidade,
    ROUND(SUM(i.amount), 2) AS valor_total
FROM payment_tickets pt
JOIN invoices i ON i.id = pt.invoice_id
GROUP BY pt.status
ORDER BY quantidade DESC;

-- 4.2: Faturas por mês de emissão
SELECT
    i.issue_month,
    COUNT(*) AS qtd_notas,
    ROUND(SUM(i.amount), 2) AS valor_total
FROM invoices i
GROUP BY i.issue_month
ORDER BY i.issue_month;

-- 4.3: Fornecedores com múltiplas notas no mesmo mês
SELECT
    s.name AS fornecedor,
    i.issue_month,
    COUNT(*) AS qtd_notas,
    ROUND(SUM(i.amount), 2) AS valor_mes
FROM invoices i
JOIN suppliers s ON s.id = i.supplier_id
GROUP BY s.id, i.issue_month
HAVING COUNT(*) > 1
ORDER BY valor_mes DESC;
