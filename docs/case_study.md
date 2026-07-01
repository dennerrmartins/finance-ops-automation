# Case Study — Finance Ops Automation

## Contexto

Analista na área **CMEF** (Comercial, Marketing e Experiência da Família) em empresa de educação. Atua em duas camadas:

1. **Operacional** — automação de NF-e, organização documental, tickets de pagamento  
2. **Gerencial** — análise da **DRE** em painel de BI corporativo (REAL / ORÇADO / A-1 / EBITDA)

> O painel DRE com contas gerenciais, filtros de marca/filial/CC e visões de variação **já existe na empresa**. O analista **interpreta, ajusta orçado e explica desvios** — não necessariamente constrói o BI.

## Problema de negócio

1. NFs em múltiplos formatos (PDF, XML, links) sem padronização  
2. Dificuldade de conciliar gastos operacionais com linhas da DRE  
3. Necessidade de explicar **Δ R-ORÇ** e impacto no **EBITDA** para gestão  
4. Risco de duplicidade de pagamento  

## O que o analista faz na DRE (indicadores)

| Indicador | Leitura |
|-----------|---------|
| **REAL** | Quanto foi executado no período |
| **ORÇADO** | Meta — sujeita a ajustes pelo analista |
| **Δ R-ORÇ / Δ %** | Estouro ou economia vs plano |
| **A-1** | Comparação com ano anterior |
| **04. SG&A → Vendas & Marketing** | Drill-down de despesas comerciais |
| **EBITDA (S/ Rateio)** | Resultado operacional antes de CSC |
| **EBITDA Total** | Resultado após rateios corporativos |

### Linhas CMEF monitoradas

- Marketing (`04.01.01`)  
- Comercial (`04.01.02`)  
- Experiência Da Família (`04.01.03`)  
- Central De Receitas (`04.01.04`)  

## Solução técnica (o que o analista construiu)

### Automação NF-e (Python)
- Gmail API → extração → biblioteca padronizada → CSV auditável  
- Anti-duplicata por chave NF-e, CNPJ+número e hash  

### Análise SQL (este repositório)
- Réplica analítica da lógica DRE com **dados fictícios**  
- Queries de REAL vs ORÇADO, A-1 e EBITDA  
- Documentação em `docs/dre_indicators.md`  

## Resultados reais (anonimizados)

| Métrica | Valor |
|---------|-------|
| Registros auditáveis (NF) | 5.900+ |
| Documentos organizados | 1.900+ |
| Fornecedores mapeados | 72 |

## Demo pública

| Métrica | Valor |
|---------|-------|
| Contas na DRE sintética | 9 |
| Linhas CMEF com análise | 4 |
| Queries SQL documentadas | 17+ |

## Diferencial para recrutador

- Entende **DRE gerencial** e indicadores de FP&A  
- Conecta **operação** (NF, pagamento) com **gestão** (orçado, EBITDA)  
- Automatiza o que é repetitivo e analisa o que importa para decisão  
