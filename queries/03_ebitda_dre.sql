-- =============================================================================
-- 03 — EBITDA e leitura gerencial da DRE
-- =============================================================================

-- 3.1: EBITDA sem rateio CSC vs EBITDA Total (estrutura típica de DRE gerencial)
SELECT
    a.account_name AS indicador,
    ROUND(SUM(p.real_amount), 2) AS real_ytd,
    ROUND(SUM(p.budget_amount), 2) AS orcado_ytd,
    ROUND(SUM(p.real_amount) - SUM(p.budget_amount), 2) AS delta_r_orc,
    ROUND(
        100.0 * (SUM(p.real_amount) - SUM(p.budget_amount)) / NULLIF(SUM(p.budget_amount), 0),
        2
    ) AS delta_pct_orc
FROM dre_performance p
JOIN dre_accounts a ON a.account_code = p.account_code
WHERE a.account_code IN ('EBITDA_SRA', 'EBITDA_TOTAL')
GROUP BY a.account_code, a.account_name
ORDER BY a.account_name;

-- 3.2: Margem EBITDA sobre receita líquida sintética (MG % simplificada)
SELECT
    p.month,
    ROUND(r.real_amount, 2) AS receita_liquida,
    ROUND(e.real_amount, 2) AS ebitda_total,
    ROUND(100.0 * e.real_amount / NULLIF(r.real_amount, 0), 2) AS mg_ebitda_pct,
    ROUND(e.real_amount - e.budget_amount, 2) AS delta_ebitda_vs_orcado
FROM dre_performance e
JOIN dre_performance r ON r.month = e.month AND r.account_code = '03'
WHERE e.account_code = 'EBITDA_TOTAL'
ORDER BY e.month;

-- 3.3: Impacto do SG&A (04) no EBITDA — leitura mês a mês
SELECT
    p.month,
    ROUND(sga.real_amount, 2) AS sga_real,
    ROUND(ebitda.real_amount, 2) AS ebitda_total,
    ROUND(
        100.0 * ABS(sga.real_amount) / NULLIF(ABS(ebitda.real_amount), 0),
        2
    ) AS sga_pct_sobre_ebitda
FROM dre_performance p
JOIN dre_performance sga ON sga.month = p.month AND sga.account_code = '04'
JOIN dre_performance ebitda ON ebitda.month = p.month AND ebitda.account_code = 'EBITDA_TOTAL'
ORDER BY p.month;

-- 3.4: Variação vs ano anterior (A-1) nas linhas CMEF
SELECT
    a.account_name AS linha_cmef,
    ROUND(SUM(p.real_amount), 2) AS real_ytd,
    ROUND(SUM(p.prior_year_amount), 2) AS a1_ytd,
    ROUND(SUM(p.real_amount) - SUM(p.prior_year_amount), 2) AS delta_r_a1,
    ROUND(
        100.0 * (SUM(p.real_amount) - SUM(p.prior_year_amount))
        / NULLIF(ABS(SUM(p.prior_year_amount)), 0),
        2
    ) AS delta_pct_a1
FROM dre_performance p
JOIN dre_accounts a ON a.account_code = p.account_code
WHERE a.account_code IN ('04.01.01', '04.01.02', '04.01.03')
GROUP BY a.account_code, a.account_name
ORDER BY delta_pct_a1;
