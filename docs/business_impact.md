# Impacto de negócio — NF Agent (dados anonimizados)

> Métricas de **operação real**. Repositório público usa apenas dados sintéticos.

---

## Problema antes da automação

| Dor | Efeito |
|-----|--------|
| NFs espalhadas no Gmail | Tempo perdido procurando documento |
| Pastas sem padrão | Auditoria e pagamento mais lentos |
| Mesma NF reenviada | Risco de pagamento em duplicidade |
| Dados não estruturados | Dificuldade de cruzar com orçado x realizado na DRE |

---

## Solução implementada

Pipeline **NF Agent**: Gmail → extração → anti-duplicata → biblioteca padronizada → CSV auditável.

---

## Resultados (produção — anonimizado)

| Métrica | Valor |
|---------|-------|
| Registros auditáveis no CSV | **+5.900** |
| Documentos organizados com sucesso | **+1.900** |
| Fornecedores mapeados | **72** |
| Arquivos na biblioteca documental | **~1.500** |

---

## Impacto operacional (qualitativo)

- **Redução de trabalho manual** na busca e organização de NF-e
- **Trilha de auditoria** para conferência de pagamentos e tickets
- **Padronização** `Fornecedor/AAAA.MM.DD/arquivo` para toda a área CMEF
- **Base operacional** para conciliar gastos com linhas da DRE (Marketing, Comercial, Exp. Família)

---

## Impacto gerencial (DRE)

O analista utiliza o painel de BI corporativo para:

- REAL vs ORÇADO por linha de conta
- Variação vs ano anterior (A-1)
- Leitura de EBITDA e pressão de SG&A / Vendas & Marketing

O NF Agent **alimenta a camada operacional**; a DRE **orienta a decisão gerencial**.

---

## O que este repo público demonstra

- Arquitetura reprodutível (modo demo)
- Queries SQL da lógica DRE com dados fictícios
- Testes automatizados dos módulos core
- Documentação para entrevista técnica e de negócio

**Não expõe:** e-mails, CNPJs reais, valores de orçamento ou XMLs de fornecedores.
