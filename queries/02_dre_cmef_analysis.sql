-- =============================================================================
-- 02 — DRE Gerencial: REAL vs ORÇADO vs A-1 (CMEF / Vendas & Marketing)
-- Réplica analítica do tipo de visão usada em BI corporativo (dados sintéticos).
-- O profissional analisa e ajusta o orçado; o painel DRE é ferramenta existente.
-- =============================================================================

-- 2.1: Drill-down SG&A → Vendas & Marketing → linhas CMEF (visão acumulada YTD)
SELECT
    a.account_code,
    a.account_name,
    ROUND(SUM(p.real_amount), 2) AS real_ytd,
    ROUND(SUM(p.budget_amount), 2) AS orcado_ytd,
    ROUND(SUM(p.real_amount) - SUM(p.budget_amount), 2) AS delta_r_orc,
    ROUND(
        100.0 * (SUM(p.real_amount) - SUM(p.budget_amount)) / NULLIF(SUM(p.budget_amount), 0),
        2
    ) AS delta_pct_orc,
    ROUND(SUM(p.prior_year_amount), 2) AS a1_ytd,
    ROUND(SUM(p.real_amount) - SUM(p.prior_year_amount), 2) AS delta_r_a1,
    ROUND(
        100.0 * (SUM(p.real_amount) - SUM(p.prior_year_amount)) / NULLIF(ABS(SUM(p.prior_year_amount)), 0),
        2
    ) AS delta_pct_a1
FROM dre_accounts a
JOIN dre_performance p ON p.account_code = a.account_code
WHERE a.account_code IN (
    '04', '04.01', '04.01.01', '04.01.02', '04.01.03', '04.01.04'
)
GROUP BY a.account_code, a.account_name, a.sort_order
ORDER BY a.sort_order;

-- 2.2: CMEF — Marketing, Comercial e Experiência da Família (mês a mês)
SELECT
    a.account_name AS linha_cmef,
    p.month,
    ROUND(p.real_amount, 2) AS real,
    ROUND(p.budget_amount, 2) AS orcado,
    ROUND(p.real_amount - p.budget_amount, 2) AS delta_r_orc,
    ROUND(
        100.0 * (p.real_amount - p.budget_amount) / NULLIF(p.budget_amount, 0),
        2
    ) AS delta_pct_orc
FROM dre_performance p
JOIN dre_accounts a ON a.account_code = p.account_code
WHERE a.account_code IN ('04.01.01', '04.01.02', '04.01.03')
ORDER BY p.month, a.sort_order;

-- 2.3: Linhas CMEF com estouro orçamentário (REAL mais negativo que ORÇADO)
SELECT
    a.account_name AS linha_cmef,
    p.month,
    ROUND(p.real_amount, 2) AS real,
    ROUND(p.budget_amount, 2) AS orcado,
    ROUND(p.real_amount - p.budget_amount, 2) AS delta_r_orc,
    ROUND(
        100.0 * (p.real_amount - p.budget_amount) / NULLIF(p.budget_amount, 0),
        2
    ) AS delta_pct_orc
FROM dre_performance p
JOIN dre_accounts a ON a.account_code = p.account_code
WHERE a.account_code IN ('04.01.01', '04.01.02', '04.01.03')
  AND p.real_amount < p.budget_amount
ORDER BY delta_pct_orc ASC;

-- 2.4: Participação de cada linha CMEF no total de Vendas & Marketing (YTD)
WITH cmef AS (
    SELECT
        a.account_name,
        SUM(p.real_amount) AS real_ytd
    FROM dre_performance p
    JOIN dre_accounts a ON a.account_code = p.account_code
    WHERE a.account_code IN ('04.01.01', '04.01.02', '04.01.03', '04.01.04')
    GROUP BY a.account_name
)
SELECT
    account_name,
    ROUND(real_ytd, 2) AS real_ytd,
    ROUND(100.0 * real_ytd / SUM(real_ytd) OVER (), 2) AS pct_do_vendas_marketing
FROM cmef
ORDER BY real_ytd;
