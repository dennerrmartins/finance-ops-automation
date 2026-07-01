# Indicadores da DRE — o que o analista interpreta

> Este documento descreve a **leitura gerencial** que o projeto demonstra.  
> Na operação real, a DRE é visualizada em **painel de BI corporativo** (Power BI / ERP).  
> O analista **não necessariamente constrói** o dashboard — mas **analisa, ajusta orçado e explica variações**.

---

## Estrutura hierárquica (plano de contas)

```
Receita Líquida (03)
SG&A (04)
└── Vendas & Marketing (04.01)
    ├── Marketing (04.01.01)          ← CMEF
    ├── Comercial (04.01.02)          ← CMEF
    ├── Experiência Da Família (04.01.03)  ← CMEF
    └── Central De Receitas (04.01.04)
EBITDA (S/ Rateio CSC)
EBITDA Total
```

**CMEF** = Comercial + Marketing + Experiência da Família (área de atuação do analista).

---

## Colunas do painel DRE

| Coluna | Significado | Como o analista usa |
|--------|-------------|---------------------|
| **REAL** | Valor realizado no período | O que de fato aconteceu |
| **ORÇADO** | Meta orçamentária | Referência de planejamento |
| **Δ R-ORÇ** | REAL − ORÇADO | Quanto estourou ou economizou (R$) |
| **Δ %** | Variação percentual vs orçado | Prioriza onde agir |
| **A-1** | Mesmo período do ano anterior | Compara evolução histórica |
| **Δ R-A-1** | REAL − A-1 | Tendência interanual |
| **MG %** | Margem (ex.: EBITDA / Receita) | Saúde do resultado |

### Convenção de sinal (despesas)

Na DRE, despesas aparecem como **valores negativos**.  
- REAL **mais negativo** que ORÇADO → **estouro** de custo  
- REAL **menos negativo** que ORÇADO → **economia** vs plano  

---

## EBITDA

| Indicador | O que é |
|-----------|---------|
| **EBITDA (S/ Rateio CSC)** | Resultado operacional antes de rateio de custos compartilhados |
| **EBITDA Total** | EBITDA após rateios corporativos (CSC) |

O analista monitora se o **crescimento de SG&A** (especialmente Vendas & Marketing) está **pressionando** o EBITDA.

---

## Filtros típicos do painel

- **Marca / Filial** — recorte organizacional  
- **Mês / Trimestre** — visão temporal  
- **Centro de custo / Fornecedor** — drill-down operacional  
- **Tags** — classificações internas de negócio  

No projeto demo, usamos `marca = 'Marca Educação Demo'` como filtro sintético.

---

## Papel do analista vs papel do BI

| Atividade | Quem faz |
|-----------|----------|
| Construir modelo semântico / painel DRE | Time de BI / Controladoria |
| **Analisar REAL vs ORÇADO** | **Analista de Dados / FP&A** |
| **Ajustar linhas orçamentárias** | **Analista da área (CMEF)** |
| Automatizar NF-e e pagamentos | Analista + automação (este projeto) |
| Explicar variação para gestão | Analista |

---

## Conexão operacional → gerencial

```
NF-e processada → fornecedor → linha CMEF → REAL na DRE
Ajuste de orçado → atualiza coluna ORÇADO
Comparativo A-1 → visão de tendência no painel
```

O repositório replica essa lógica em **SQL + dados fictícios** para portfólio.
