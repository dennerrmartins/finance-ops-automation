# Release v1.0-demo

**Data:** 2026-07-01  
**Tipo:** Demo pública com dados 100% sintéticos (production-inspired)

## O que inclui

- **NF Agent** — pipeline demo (`run_demo.py`) com extração XML, anti-duplicata, organização por fornecedor/data e CSV de auditoria
- **SQLite** — schema de invoices + DRE gerencial sintética (REAL / ORÇADO / EBITDA / CMEF)
- **SQL** — 5 módulos de queries documentados + `run_queries.py`
- **Testes** — `python -m unittest discover -s tests -v` (8 testes)
- **Docs** — arquitetura, impacto de negócio, pitch de entrevista, case study

## Quick start

```bash
pip install -r requirements.txt
python run_demo.py --reset
python create_database.py
python run_queries.py
python -m unittest discover -s tests -v
```

## Produção real (referência anonimizada)

Inspirado em automação corporativa: +5.900 registros · +1.900 NFs · 72 fornecedores.  
Modo Gmail documentado em `docs/nf_agent_architecture.md` (requer credenciais próprias).

## Limitações desta release

- Dados sintéticos apenas — sem exposição de informações reais
- Modo Gmail não inclui credenciais
- Sem dashboard Power BI embutido (lógica DRE via SQL)
