# Finance Ops Automation — Relatório SQL

> Gerado em **01/07/2026 10:39** · SQLite · dados sintéticos de demonstração

> **Aviso:** projeto educacional de portfólio. Não utiliza dados reais de empresas.

---

## Sumário executivo

- **Camada operacional:** 15 NFs · R$ 213,802.40 em fornecedores (demo)
- **Camada gerencial (DRE sintética):** 9 contas · leitura REAL / ORÇADO / A-1
- **Linhas CMEF acima do orçado:** 1 ocorrências
- **EBITDA Total YTD (demo):** REAL R$ 70,731,435.00 · ORÇADO R$ 67,390,000.00
- **Papel do analista:** interpretar variações e ajustar orçado — painel DRE é ferramenta corporativa existente

---

## 01 — Análise de Fornecedores (operacional)

### 1.1: Top fornecedores por valor total pago

```sql
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
```

| fornecedor | area | qtd_notas | valor_total |
| --- | --- | --- | --- |
| Fornecedor Alpha Ltda | Comercial | 4 | 77650.25 |
| Eventos Zeta Producoes Ltda | Experiencia Familia | 2 | 41300.00 |
| Agencia Beta Marketing SA | Marketing | 3 | 40400.50 |
| Consultoria Delta Ltda | Experiencia Familia | 2 | 29000.75 |
| Tech Epsilon Servicos SA | Comercial | 2 | 16050.90 |
| Studio Gamma Design ME | Marketing | 2 | 9400.00 |

### 1.2: Concentração de gastos por área

```sql
SELECT
    s.area,
    COUNT(DISTINCT s.id) AS fornecedores,
    ROUND(SUM(i.amount), 2) AS gasto_total,
    ROUND(100.0 * SUM(i.amount) / (SELECT SUM(amount) FROM invoices), 2) AS pct_do_total
FROM invoices i
JOIN suppliers s ON s.id = i.supplier_id
GROUP BY s.area
ORDER BY gasto_total DESC;
```

| area | fornecedores | gasto_total | pct_do_total |
| --- | --- | --- | --- |
| Comercial | 2 | 93701.15 | 43.83 |
| Experiencia Familia | 2 | 70300.75 | 32.88 |
| Marketing | 2 | 49800.50 | 23.29 |

### 1.3: Ticket médio por fornecedor

```sql
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
```

| fornecedor | ticket_medio | menor_nf | maior_nf |
| --- | --- | --- | --- |
| Eventos Zeta Producoes Ltda | 20650.00 | 12400.00 | 28900.00 |
| Fornecedor Alpha Ltda | 19412.56 | 16750.25 | 22100.00 |
| Consultoria Delta Ltda | 14500.38 | 13200.00 | 15800.75 |
| Agencia Beta Marketing SA | 13466.83 | 9200.50 | 19800.00 |
| Tech Epsilon Servicos SA | 8025.45 | 7600.00 | 8450.90 |
| Studio Gamma Design ME | 4700.00 | 4300.00 | 5100.00 |

## 02 — DRE Gerencial: REAL vs ORÇADO vs A-1 (CMEF)

### 2.1: Drill-down SG&A → Vendas & Marketing → linhas CMEF (visão acumulada YTD)

```sql
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
```

| account_code | account_name | real_ytd | orcado_ytd | delta_r_orc | delta_pct_orc | a1_ytd | delta_r_a1 | delta_pct_a1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 04 | SG&A | -21950000.00 | -22710000.00 | 760000.00 | -3.35 | -20330000.00 | -1620000.00 | -7.97 |
| 04.01 | Vendas & Marketing | -16700000.00 | -17210000.00 | 510000.00 | -2.96 | -15330000.00 | -1370000.00 | -8.94 |
| 04.01.01 | Marketing | -6380000.00 | -6580000.00 | 200000.00 | -3.04 | -5750000.00 | -630000.00 | -10.96 |
| 04.01.02 | Comercial | -5340000.00 | -5500000.00 | 160000.00 | -2.91 | -4960000.00 | -380000.00 | -7.66 |
| 04.01.03 | Experiência Da Família | -3880000.00 | -3980000.00 | 100000.00 | -2.51 | -3570000.00 | -310000.00 | -8.68 |
| 04.01.04 | Central De Receitas | -1100000.00 | -1150000.00 | 50000.00 | -4.35 | -1050000.00 | -50000.00 | -4.76 |

### 2.2: CMEF — Marketing, Comercial e Experiência da Família (mês a mês)

```sql
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
```

| linha_cmef | month | real | orcado | delta_r_orc | delta_pct_orc |
| --- | --- | --- | --- | --- | --- |
| Marketing | 2026-01 | -1180000.00 | -1250000.00 | 70000.00 | -5.60 |
| Comercial | 2026-01 | -980000.00 | -1020000.00 | 40000.00 | -3.92 |
| Experiência Da Família | 2026-01 | -720000.00 | -750000.00 | 30000.00 | -4.00 |
| Marketing | 2026-02 | -1210000.00 | -1280000.00 | 70000.00 | -5.47 |
| Comercial | 2026-02 | -1010000.00 | -1050000.00 | 40000.00 | -3.81 |
| Experiência Da Família | 2026-02 | -740000.00 | -760000.00 | 20000.00 | -2.63 |
| Marketing | 2026-03 | -1320000.00 | -1300000.00 | -20000.00 | 1.54 |
| Comercial | 2026-03 | -1080000.00 | -1100000.00 | 20000.00 | -1.82 |
| Experiência Da Família | 2026-03 | -780000.00 | -800000.00 | 20000.00 | -2.50 |
| Marketing | 2026-04 | -1280000.00 | -1350000.00 | 70000.00 | -5.19 |
| Comercial | 2026-04 | -1120000.00 | -1150000.00 | 30000.00 | -2.61 |
| Experiência Da Família | 2026-04 | -810000.00 | -820000.00 | 10000.00 | -1.22 |
| Marketing | 2026-05 | -1390000.00 | -1400000.00 | 10000.00 | -0.71 |
| Comercial | 2026-05 | -1150000.00 | -1180000.00 | 30000.00 | -2.54 |
| Experiência Da Família | 2026-05 | -830000.00 | -850000.00 | 20000.00 | -2.35 |

### 2.3: Linhas CMEF com estouro orçamentário (REAL mais negativo que ORÇADO)

```sql
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
```

| linha_cmef | month | real | orcado | delta_r_orc | delta_pct_orc |
| --- | --- | --- | --- | --- | --- |
| Marketing | 2026-03 | -1320000.00 | -1300000.00 | -20000.00 | 1.54 |

### 2.4: Participação de cada linha CMEF no total de Vendas & Marketing (YTD)

```sql
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
```

| account_name | real_ytd | pct_do_vendas_marketing |
| --- | --- | --- |
| Marketing | -6380000.00 | 38.20 |
| Comercial | -5340000.00 | 31.98 |
| Experiência Da Família | -3880000.00 | 23.23 |
| Central De Receitas | -1100000.00 | 6.59 |

## 03 — EBITDA e leitura gerencial

### 3.1: EBITDA sem rateio CSC vs EBITDA Total (estrutura típica de DRE gerencial)

```sql
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
```

| indicador | real_ytd | orcado_ytd | delta_r_orc | delta_pct_orc |
| --- | --- | --- | --- | --- |
| EBITDA (S/ Rateio CSC) | 71631435.00 | 68290000.00 | 3341435.00 | 4.89 |
| EBITDA Total | 70731435.00 | 67390000.00 | 3341435.00 | 4.96 |

### 3.2: Margem EBITDA sobre receita líquida sintética (MG % simplificada)

```sql
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
```

**Erro:** no such column: p.month

### 3.3: Impacto do SG&A (04) no EBITDA — leitura mês a mês

```sql
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
```

_45 linhas — exibindo 20_

| month | sga_real | ebitda_total | sga_pct_sobre_ebitda |
| --- | --- | --- | --- |
| 2026-01 | -4140000.00 | 14457282.00 | 28.64 |
| 2026-01 | -4140000.00 | 14457282.00 | 28.64 |
| 2026-01 | -4140000.00 | 14457282.00 | 28.64 |
| 2026-01 | -4140000.00 | 14457282.00 | 28.64 |
| 2026-01 | -4140000.00 | 14457282.00 | 28.64 |
| 2026-01 | -4140000.00 | 14457282.00 | 28.64 |
| 2026-01 | -4140000.00 | 14457282.00 | 28.64 |
| 2026-01 | -4140000.00 | 14457282.00 | 28.64 |
| 2026-01 | -4140000.00 | 14457282.00 | 28.64 |
| 2026-02 | -4225000.00 | 14417593.00 | 29.30 |
| 2026-02 | -4225000.00 | 14417593.00 | 29.30 |
| 2026-02 | -4225000.00 | 14417593.00 | 29.30 |
| 2026-02 | -4225000.00 | 14417593.00 | 29.30 |
| 2026-02 | -4225000.00 | 14417593.00 | 29.30 |
| 2026-02 | -4225000.00 | 14417593.00 | 29.30 |
| 2026-02 | -4225000.00 | 14417593.00 | 29.30 |
| 2026-02 | -4225000.00 | 14417593.00 | 29.30 |
| 2026-02 | -4225000.00 | 14417593.00 | 29.30 |
| 2026-03 | -4450000.00 | 13909483.00 | 31.99 |
| 2026-03 | -4450000.00 | 13909483.00 | 31.99 |

### 3.4: Variação vs ano anterior (A-1) nas linhas CMEF

```sql
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
```

| linha_cmef | real_ytd | a1_ytd | delta_r_a1 | delta_pct_a1 |
| --- | --- | --- | --- | --- |
| Marketing | -6380000.00 | -5750000.00 | -630000.00 | -10.96 |
| Experiência Da Família | -3880000.00 | -3570000.00 | -310000.00 | -8.68 |
| Comercial | -5340000.00 | -4960000.00 | -380000.00 | -7.66 |

## 04 — Operações de Pagamento

### 4.1: Status dos tickets de pagamento

```sql
SELECT
    pt.status,
    COUNT(*) AS quantidade,
    ROUND(SUM(i.amount), 2) AS valor_total
FROM payment_tickets pt
JOIN invoices i ON i.id = pt.invoice_id
GROUP BY pt.status
ORDER BY quantidade DESC;
```

| status | quantidade | valor_total |
| --- | --- | --- |
| pago | 15 | 213802.40 |

### 4.2: Faturas por mês de emissão

```sql
SELECT
    i.issue_month,
    COUNT(*) AS qtd_notas,
    ROUND(SUM(i.amount), 2) AS valor_total
FROM invoices i
GROUP BY i.issue_month
ORDER BY i.issue_month;
```

| issue_month | qtd_notas | valor_total |
| --- | --- | --- |
| 2026-01 | 3 | 32000.50 |
| 2026-02 | 3 | 45500.75 |
| 2026-03 | 3 | 57050.25 |
| 2026-04 | 3 | 26750.90 |
| 2026-05 | 3 | 52500.00 |

### 4.3: Fornecedores com múltiplas notas no mesmo mês

```sql
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
```

_Sem resultados._

## 05 — Sumário Executivo

### 5.1: KPIs gerais do pipeline

```sql
SELECT
    (SELECT COUNT(*) FROM invoices WHERE status = 'sucesso') AS notas_processadas,
    (SELECT COUNT(DISTINCT supplier_id) FROM invoices) AS fornecedores_ativos,
    (SELECT ROUND(SUM(amount), 2) FROM invoices) AS gasto_total,
    (SELECT COUNT(*) FROM payment_tickets WHERE status = 'pago') AS tickets_pagos;
```

| notas_processadas | fornecedores_ativos | gasto_total | tickets_pagos |
| --- | --- | --- | --- |
| 15 | 6 | 213802.40 | 15 |

### 5.2: Ranking de áreas por eficiência orçamentária (menor estouro primeiro)

```sql
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
```

| area | orcado_total | realizado_total | pct_consumido |
| --- | --- | --- | --- |
| Comercial | 298000.00 | 93701.15 | 31.44 |
| Marketing | 152000.00 | 49800.50 | 32.76 |
| Experiencia Familia | 171000.00 | 70300.75 | 41.11 |

### 5.3: CTE — visão consolidada CMEF

```sql
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
```

| area | month | orcado | realizado | status_linha |
| --- | --- | --- | --- | --- |
| Comercial | 2026-01 | 45000.00 | 18500.00 | ABAIXO |
| Experiencia Familia | 2026-01 | 30000.00 | 0.00 | ABAIXO |
| Marketing | 2026-01 | 22000.00 | 13500.50 | ABAIXO |
| Comercial | 2026-02 | 48000.00 | 29700.00 | ABAIXO |
| Experiencia Familia | 2026-02 | 32000.00 | 15800.75 | ABAIXO |
| Marketing | 2026-02 | 24000.00 | 0.00 | ABAIXO |
| Comercial | 2026-03 | 50000.00 | 16750.25 | ABAIXO |
| Experiencia Familia | 2026-03 | 35000.00 | 28900.00 | ABAIXO |
| Marketing | 2026-03 | 26000.00 | 11400.00 | ABAIXO |
| Comercial | 2026-04 | 52000.00 | 8450.90 | ABAIXO |
| Experiencia Familia | 2026-04 | 36000.00 | 13200.00 | ABAIXO |
| Marketing | 2026-04 | 28000.00 | 5100.00 | ABAIXO |
| Comercial | 2026-05 | 55000.00 | 20300.00 | ABAIXO |
| Experiencia Familia | 2026-05 | 38000.00 | 12400.00 | ABAIXO |
| Marketing | 2026-05 | 30000.00 | 19800.00 | ABAIXO |

### 5.4: Ponte operacional → DRE — fornecedor mapeado à linha CMEF

```sql
SELECT
    s.name AS fornecedor,
    a.account_name AS linha_dre_cmef,
    ROUND(SUM(i.amount), 2) AS real_operacional_nf
FROM invoices i
JOIN suppliers s ON s.id = i.supplier_id
JOIN dre_accounts a ON a.account_code = s.dre_account_code
GROUP BY s.id, a.account_name
ORDER BY real_operacional_nf DESC;
```

| fornecedor | linha_dre_cmef | real_operacional_nf |
| --- | --- | --- |
| Fornecedor Alpha Ltda | Comercial | 77650.25 |
| Eventos Zeta Producoes Ltda | Experiência Da Família | 41300.00 |
| Agencia Beta Marketing SA | Marketing | 40400.50 |
| Consultoria Delta Ltda | Experiência Da Família | 29000.75 |
| Tech Epsilon Servicos SA | Comercial | 16050.90 |
| Studio Gamma Design ME | Marketing | 9400.00 |

