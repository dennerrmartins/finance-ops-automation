"""Executa queries SQL e gera output/RESULTS.md."""

import re
import sqlite3
from datetime import datetime
from pathlib import Path

import config

ROOT = Path(__file__).parent
QUERIES_DIR = ROOT / "queries"
OUTPUT_FILE = config.OUTPUT_DIR / "RESULTS.md"

FILE_LABELS = {
    "01_supplier_analysis.sql": "01 — Análise de Fornecedores (operacional)",
    "02_dre_cmef_analysis.sql": "02 — DRE Gerencial: REAL vs ORÇADO vs A-1 (CMEF)",
    "03_ebitda_dre.sql": "03 — EBITDA e leitura gerencial",
    "04_payment_operations.sql": "04 — Operações de Pagamento",
    "05_executive_summary.sql": "05 — Sumário Executivo",
}

QUERY_TITLE = re.compile(r"^--\s*\d+\.\d+:")


def parse_queries(content: str) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = []
    current_title = "Query"
    current_lines: list[str] = []

    for line in content.splitlines():
        stripped = line.strip()
        if QUERY_TITLE.match(stripped):
            if current_lines:
                block_sql = "\n".join(current_lines).strip()
                if "SELECT" in block_sql.upper():
                    blocks.append((current_title, block_sql))
                current_lines = []
            current_title = stripped.lstrip("- ").strip()
        elif stripped and not stripped.startswith("-- =="):
            current_lines.append(line)

    if current_lines:
        block_sql = "\n".join(current_lines).strip()
        if "SELECT" in block_sql.upper():
            blocks.append((current_title, block_sql))
    return blocks


def format_cell(value) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def rows_to_markdown(headers: list[str], rows: list[tuple]) -> str:
    if not rows:
        return "_Sem resultados._\n"
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(format_cell(v) for v in row) + " |")
    return "\n".join(lines) + "\n"


def executive_summary(conn: sqlite3.Connection) -> str:
    inv = conn.execute(
        "SELECT COUNT(*), ROUND(SUM(amount),2) FROM invoices WHERE status='sucesso'"
    ).fetchone()
    dre_lines = conn.execute("SELECT COUNT(*) FROM dre_accounts").fetchone()[0]
    over = conn.execute(
        """
        SELECT COUNT(*) FROM dre_performance p
        JOIN dre_accounts a ON a.account_code = p.account_code
        WHERE a.account_code IN ('04.01.01','04.01.02','04.01.03')
          AND p.real_amount < p.budget_amount
        """
    ).fetchone()[0]
    ebitda = conn.execute(
        """
        SELECT ROUND(SUM(real_amount),2), ROUND(SUM(budget_amount),2)
        FROM dre_performance WHERE account_code = 'EBITDA_TOTAL'
        """
    ).fetchone()

    return (
        f"- **Camada operacional:** {inv[0]} NFs · R$ {inv[1]:,.2f} em fornecedores (demo)\n"
        f"- **Camada gerencial (DRE sintética):** {dre_lines} contas · leitura REAL / ORÇADO / A-1\n"
        f"- **Linhas CMEF acima do orçado:** {over} ocorrências\n"
        f"- **EBITDA Total YTD (demo):** REAL R$ {ebitda[0]:,.2f} · ORÇADO R$ {ebitda[1]:,.2f}\n"
        f"- **Papel do analista:** interpretar variações e ajustar orçado — painel DRE é ferramenta corporativa existente\n"
    )


def build_report() -> str:
    conn = sqlite3.connect(config.DB_PATH)
    parts = [
        "# Finance Ops Automation — Relatório SQL\n\n",
        f"> Gerado em **{datetime.now().strftime('%d/%m/%Y %H:%M')}** · "
        "SQLite · dados sintéticos de demonstração\n\n",
        "> **Aviso:** projeto educacional de portfólio. Não utiliza dados reais de empresas.\n\n",
        "---\n\n## Sumário executivo\n\n",
        executive_summary(conn),
        "\n---\n\n",
    ]

    for filename in sorted(QUERIES_DIR.glob("*.sql")):
        label = FILE_LABELS.get(filename.name, filename.stem)
        parts.append(f"## {label}\n\n")
        for title, sql in parse_queries(filename.read_text(encoding="utf-8")):
            parts.append(f"### {title}\n\n```sql\n{sql.strip()}\n```\n\n")
            try:
                cur = conn.execute(sql)
                rows = cur.fetchall()
                headers = [d[0] for d in cur.description] if cur.description else []
                if len(rows) > 20:
                    parts.append(f"_{len(rows)} linhas — exibindo 20_\n\n")
                    rows = rows[:20]
                parts.append(rows_to_markdown(headers, rows) + "\n")
            except sqlite3.Error as exc:
                parts.append(f"**Erro:** {exc}\n\n")

    conn.close()
    return "".join(parts)


def main() -> None:
    if not config.DB_PATH.exists():
        raise SystemExit("Banco não encontrado. Rode: python create_database.py")
    config.OUTPUT_DIR.mkdir(exist_ok=True)
    OUTPUT_FILE.write_text(build_report(), encoding="utf-8")
    print(f"Relatório: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
