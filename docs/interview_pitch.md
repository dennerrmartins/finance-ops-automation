# Como falar deste projeto em entrevista

## Pitch de 30 segundos

> "Na área CMEF, automatizei a captura de notas fiscais com Python e Gmail API: o agente lê o e-mail, extrai PDF e XML, bloqueia duplicata e organiza tudo em biblioteca padronizada com CSV de auditoria. Na operação real foram mais de 1.900 documentos e 72 fornecedores. No dia a dia também analiso a DRE no Power BI — REAL vs orçado, EBITDA — nas linhas de Marketing, Comercial e Experiência da Família. Publiquei no GitHub a arquitetura em modo demo com análise SQL da DRE."

---

## Se perguntarem: "O que você automatizou?"

- Monitoramento de e-mails com termos de NF-e / fatura / boleto
- Download de anexos PDF/XML
- Extração de CNPJ, número, valor e chave de acesso
- **3 camadas de anti-duplicata:** chave NF-e, CNPJ+número, hash MD5
- Organização: `Fornecedor/AAAA.MM.DD/arquivo`
- Planilha CSV com status, remetente, valor e caminho do arquivo

---

## Se perguntarem: "Qual foi o impacto?"

Use números (anonimizados):

- +5.900 registros auditáveis
- +1.900 NFs organizadas
- 72 fornecedores mapeados
- Menos risco de pagar NF duplicada
- Menos tempo procurando documento no Gmail

📖 Detalhes: [`business_impact.md`](business_impact.md)

---

## Se perguntarem: "Você criou o painel DRE?"

> "Não modelei o BI — isso é do time de dados/controladoria. **Eu analiso** o painel: interpreto REAL vs ORÇADO, ajusto orçado por linha quando necessário, explico variação para gestão e conecto os pagamentos com as notas que o NF Agent organizou."

---

## Se perguntarem: "Mostra código / GitHub"

1. **Projeto principal:** github.com/dennerrmartins/finance-ops-automation  
2. Mostrar: `nf_agent/`, `docs/nf_agent_architecture.md`, `output/RESULTS.md`  
3. Rodar ao vivo: `python run_demo.py --reset`  
4. **Projeto secundário (SQL finanças):** github.com/dennerrmartins/b3-financial-analysis  

---

## Perguntas técnicas prováveis

| Pergunta | Resposta curta |
|----------|----------------|
| Por que Python? | Integração Gmail API, parsing XML/PDF, automação de arquivos |
| Como detecta duplicata? | Chave 44 dígitos → CNPJ+NF → hash do arquivo |
| Onde persiste estado? | `nf_registry.json` + CSV de auditoria |
| SQL usado para quê? | DRE: REAL/ORÇADO, EBITDA, drill-down CMEF |
| Power BI? | Dashboards NPS, evasão, captação + análise DRE no BI corporativo |

---

## O que NÃO dizer

- ❌ "Sou iniciante em dados"
- ❌ "É só um projeto de estudo" (sobre o NF Agent)
- ❌ "Criei o dashboard DRE"
- ❌ Compartilhar dados reais da empresa

## O que DIZER

- ✅ "Analista de Dados/BI com foco em finanças e automação operacional"
- ✅ "Automação em produção + análise DRE + SQL reprodutível"
- ✅ "Power BI + DRE + SQL + Python + métricas auditáveis"
