# NF Agent — Arquitetura (Demo vs Produção)

O **NF Agent** é o agente Python que automatiza captura, extração e organização de notas fiscais.  
Este repositório contém a **mesma arquitetura** usada em produção, com dois modos de execução.

---

## Visão geral

```
                    ┌─────────────────────────────────────┐
                    │           NF AGENT (Python)          │
                    └─────────────────────────────────────┘
                                      │
          ┌───────────────────────────┼───────────────────────────┐
          ▼                           ▼                           ▼
   ┌─────────────┐            ┌─────────────┐            ┌─────────────┐
   │   Entrada   │            │  Extração   │            │ Organização │
   │ Gmail / Demo│───────────▶│ PDF / XML   │───────────▶│ Biblioteca  │
   └─────────────┘            └─────────────┘            └─────────────┘
          │                           │                           │
          └───────────────────────────┼───────────────────────────┘
                                      ▼
                            ┌─────────────────┐
                            │ Anti-duplicata  │
                            │ + CSV auditoria │
                            └─────────────────┘
                                      │
                                      ▼
                            ┌─────────────────┐
                            │ SQLite + DRE    │
                            │ (análise CMEF)  │
                            └─────────────────┘
```

---

## Modo Demo (portfólio — sem credenciais)

| Item | Detalhe |
|------|---------|
| **Comando** | `python run_demo.py --reset` |
| **Entrada** | `demo/inbox/` — XMLs sintéticos |
| **Saída** | `output/notas/`, `output/planilhas/invoices_audit.csv` |
| **Uso** | GitHub, entrevistas, reprodutibilidade |

```bash
pip install -r requirements.txt
python run_demo.py --reset
python create_database.py
python run_queries.py
```

---

## Modo Produção (Gmail API)

| Item | Detalhe |
|------|---------|
| **Comando** | `python run_gmail.py` |
| **Entrada** | Caixa de entrada Gmail (query configurável) |
| **Credenciais** | `credentials/credentials.json` + `token.json` (gitignored) |
| **Uso** | Ambiente corporativo real (não publicar dados) |

### Setup Gmail

1. Criar projeto no [Google Cloud Console](https://console.cloud.google.com/)
2. Ativar **Gmail API**
3. Criar credencial OAuth 2.0 (Desktop)
4. Baixar JSON → `credentials/credentials.json`
5. Configurar ambiente:

```bash
cp .env.example .env
pip install -r requirements.txt -r requirements-gmail.txt
python run_gmail.py
```

Na primeira execução, o navegador abre para autorização OAuth.

---

## Módulos (`nf_agent/`)

| Módulo | Função |
|--------|--------|
| `extractor.py` | Extrai CNPJ, número, valor, chave de PDF/XML |
| `organizer.py` | `Fornecedor/AAAA.MM.DD/arquivo` |
| `duplicate_checker.py` | Chave NF-e · CNPJ+número · hash MD5 |
| `csv_export.py` | Trilha de auditoria |
| `processor.py` | Pipeline demo (pasta local) |
| `gmail_client.py` | Autenticação e API Gmail |
| `gmail_processor.py` | Pipeline produção (Gmail → biblioteca) |

---

## Anti-duplicata (3 camadas)

1. **Chave de acesso NF-e** (44 dígitos) — mais confiável  
2. **CNPJ emitente + número da NF**  
3. **Hash MD5 do arquivo** — mesmo PDF reenviado em threads diferentes  

Registro persistido em `nf_registry.json`.

---

## Métricas reais (produção — anonimizadas)

| Métrica | Valor |
|---------|-------|
| Registros auditáveis | 5.900+ |
| Documentos organizados | 1.900+ |
| Fornecedores mapeados | 72 |
| Arquivos na biblioteca | 1.500+ |

---

## Conexão com DRE / CMEF

```
NF Agent (operacional)              Analista (gerencial)
─────────────────────              ────────────────────
Fornecedor → linha CMEF      →     REAL na DRE (painel BI)
CSV auditável                →     Conferência de pagamentos
Ticket de pagamento          →     ORÇADO x REALIZADO, EBITDA
```

O analista **interpreta** o painel DRE (REAL / ORÇADO / A-1 / EBITDA).  
O NF Agent **alimenta** a camada operacional com documentos organizados.

📖 Indicadores DRE: [`dre_indicators.md`](dre_indicators.md)

---

## O que NÃO versionar

- `credentials/` (OAuth)
- `.env`
- `output/notas/` com XMLs/PDFs reais
- Logs com e-mails ou CNPJs de fornecedores reais
