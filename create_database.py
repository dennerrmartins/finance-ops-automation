"""Cria banco SQLite: NF-e (operacional) + DRE gerencial sintética (análise CMEF)."""

import csv
import re
import sqlite3
from pathlib import Path

import config
from nf_agent.extractor import parse_amount

SUPPLIER_AREAS = {
    "Fornecedor Alpha Ltda": "Comercial",
    "Agencia Beta Marketing SA": "Marketing",
    "Studio Gamma Design ME": "Marketing",
    "Consultoria Delta Ltda": "Experiencia Familia",
    "Tech Epsilon Servicos SA": "Comercial",
    "Eventos Zeta Producoes Ltda": "Experiencia Familia",
}

AREA_TO_DRE = {
    "Marketing": "04.01.01",
    "Comercial": "04.01.02",
    "Experiencia Familia": "04.01.03",
}

BUDGET_2026 = {
    ("Comercial", "2026-01"): 45000,
    ("Comercial", "2026-02"): 48000,
    ("Comercial", "2026-03"): 50000,
    ("Comercial", "2026-04"): 52000,
    ("Comercial", "2026-05"): 55000,
    ("Marketing", "2026-01"): 22000,
    ("Marketing", "2026-02"): 24000,
    ("Marketing", "2026-03"): 26000,
    ("Marketing", "2026-04"): 28000,
    ("Marketing", "2026-05"): 30000,
    ("Experiencia Familia", "2026-01"): 30000,
    ("Experiencia Familia", "2026-02"): 32000,
    ("Experiencia Familia", "2026-03"): 35000,
    ("Experiencia Familia", "2026-04"): 36000,
    ("Experiencia Familia", "2026-05"): 38000,
}

# Plano de contas gerencial (espelha estrutura típica: SG&A → Vendas & Marketing → CMEF)
DRE_ACCOUNTS = [
    ("03", "Receita Líquida", None, 1, "revenue"),
    ("04", "SG&A", None, 1, "expense"),
    ("04.01", "Vendas & Marketing", "04", 2, "expense"),
    ("04.01.01", "Marketing", "04.01", 3, "expense"),
    ("04.01.02", "Comercial", "04.01", 3, "expense"),
    ("04.01.03", "Experiência Da Família", "04.01", 3, "expense"),
    ("04.01.04", "Central De Receitas", "04.01", 3, "expense"),
    ("EBITDA_SRA", "EBITDA (S/ Rateio CSC)", None, 1, "ebitda"),
    ("EBITDA_TOTAL", "EBITDA Total", None, 1, "ebitda"),
]

MONTHS = ["2026-01", "2026-02", "2026-03", "2026-04", "2026-05"]

def _month_key_from_path(path: str) -> str | None:
    match = re.search(r"(\d{4})\.(\d{2})\.\d{2}", path or "")
    if not match:
        return None
    return f"{match.group(1)}-{match.group(2)}"


def _seed_dre_performance(cur: sqlite3.Cursor) -> None:
    """Gera DRE sintética com lógica REAL / ORÇADO / A-1 por linha CMEF."""

    # Base mensal por linha CMEF (valores fictícios em escala corporativa)
    cmef_monthly = {
        "04.01.01": {  # Marketing
            "2026-01": (-1180000, -1250000, -1090000),
            "2026-02": (-1210000, -1280000, -1120000),
            "2026-03": (-1320000, -1300000, -1150000),
            "2026-04": (-1280000, -1350000, -1180000),
            "2026-05": (-1390000, -1400000, -1210000),
        },
        "04.01.02": {  # Comercial
            "2026-01": (-980000, -1020000, -950000),
            "2026-02": (-1010000, -1050000, -970000),
            "2026-03": (-1080000, -1100000, -990000),
            "2026-04": (-1120000, -1150000, -1010000),
            "2026-05": (-1150000, -1180000, -1040000),
        },
        "04.01.03": {  # Experiência Da Família
            "2026-01": (-720000, -750000, -680000),
            "2026-02": (-740000, -760000, -690000),
            "2026-03": (-780000, -800000, -710000),
            "2026-04": (-810000, -820000, -730000),
            "2026-05": (-830000, -850000, -760000),
        },
        "04.01.04": {  # Central De Receitas
            "2026-01": (-210000, -220000, -200000),
            "2026-02": (-215000, -225000, -205000),
            "2026-03": (-220000, -230000, -210000),
            "2026-04": (-225000, -235000, -215000),
            "2026-05": (-230000, -240000, -220000),
        },
    }

    for account, months in cmef_monthly.items():
        for month, (real, orcado, a1) in months.items():
            cur.execute(
                """
                INSERT INTO dre_performance
                (account_code, month, marca, real_amount, budget_amount, prior_year_amount)
                VALUES (?, ?, 'Marca Educação Demo', ?, ?, ?)
                """,
                (account, month, real, orcado, a1),
            )

    # Agregar Vendas & Marketing, SG&A, Receita e EBITDA
    for month in MONTHS:
        cur.execute(
            """
            SELECT SUM(real_amount), SUM(budget_amount), SUM(prior_year_amount)
            FROM dre_performance
            WHERE account_code LIKE '04.01.%' AND month = ?
            """,
            (month,),
        )
        vm_real, vm_orc, vm_a1 = cur.fetchone()
        cur.execute(
            """
            INSERT INTO dre_performance
            (account_code, month, marca, real_amount, budget_amount, prior_year_amount)
            VALUES ('04.01', ?, 'Marca Educação Demo', ?, ?, ?)
            """,
            (month, vm_real, vm_orc, vm_a1),
        )

        sga_real = vm_real - 1050000  # outras despesas SG&A fora CMEF
        sga_orc = vm_orc - 1100000
        sga_a1 = vm_a1 - 1000000
        cur.execute(
            """
            INSERT INTO dre_performance
            (account_code, month, marca, real_amount, budget_amount, prior_year_amount)
            VALUES ('04', ?, 'Marca Educação Demo', ?, ?, ?)
            """,
            (month, sga_real, sga_orc, sga_a1),
        )

        receita_real = 18500000 + (hash(month) % 400000)
        receita_orc = 18200000
        receita_a1 = 17800000
        cur.execute(
            """
            INSERT INTO dre_performance
            (account_code, month, marca, real_amount, budget_amount, prior_year_amount)
            VALUES ('03', ?, 'Marca Educação Demo', ?, ?, ?)
            """,
            (month, receita_real, receita_orc, receita_a1),
        )

        ebitda_sra = receita_real + sga_real  # despesas negativas
        ebitda_sra_orc = receita_orc + sga_orc
        ebitda_sra_a1 = receita_a1 + sga_a1
        cur.execute(
            """
            INSERT INTO dre_performance
            (account_code, month, marca, real_amount, budget_amount, prior_year_amount)
            VALUES ('EBITDA_SRA', ?, 'Marca Educação Demo', ?, ?, ?)
            """,
            (month, ebitda_sra, ebitda_sra_orc, ebitda_sra_a1),
        )

        rateio = -180000
        cur.execute(
            """
            INSERT INTO dre_performance
            (account_code, month, marca, real_amount, budget_amount, prior_year_amount)
            VALUES ('EBITDA_TOTAL', ?, 'Marca Educação Demo', ?, ?, ?)
            """,
            (month, ebitda_sra + rateio, ebitda_sra_orc + rateio, ebitda_sra_a1 + rateio),
        )


def build_database(csv_path: Path | None = None, db_path: Path = config.DB_PATH) -> Path:
    csv_path = csv_path or (config.PLANILHAS_DIR / config.CSV_FILENAME)
    if not csv_path.exists():
        raise FileNotFoundError(
            f"CSV não encontrado: {csv_path}. Execute primeiro: python run_demo.py"
        )

    config.DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE TABLE suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            cnpj TEXT,
            area TEXT NOT NULL,
            dre_account_code TEXT
        );

        CREATE TABLE invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier_id INTEGER NOT NULL,
            issue_month TEXT NOT NULL,
            issue_date TEXT,
            nf_number TEXT,
            amount REAL NOT NULL,
            status TEXT NOT NULL,
            file_path TEXT,
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
        );

        CREATE TABLE budget_lines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            area TEXT NOT NULL,
            dre_account_code TEXT,
            month TEXT NOT NULL,
            budget_amount REAL NOT NULL,
            UNIQUE(area, month)
        );

        CREATE TABLE actuals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            budget_line_id INTEGER NOT NULL,
            invoice_id INTEGER,
            amount REAL NOT NULL,
            FOREIGN KEY (budget_line_id) REFERENCES budget_lines(id),
            FOREIGN KEY (invoice_id) REFERENCES invoices(id)
        );

        CREATE TABLE payment_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER NOT NULL,
            opened_at TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (invoice_id) REFERENCES invoices(id)
        );

        CREATE TABLE dre_accounts (
            account_code TEXT PRIMARY KEY,
            account_name TEXT NOT NULL,
            parent_code TEXT,
            hierarchy_level INTEGER NOT NULL,
            account_type TEXT NOT NULL,
            sort_order INTEGER NOT NULL
        );

        CREATE TABLE dre_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_code TEXT NOT NULL,
            month TEXT NOT NULL,
            marca TEXT NOT NULL DEFAULT 'Marca Demo',
            real_amount REAL NOT NULL,
            budget_amount REAL NOT NULL,
            prior_year_amount REAL NOT NULL,
            FOREIGN KEY (account_code) REFERENCES dre_accounts(account_code),
            UNIQUE(account_code, month, marca)
        );
        """
    )

    for idx, (code, name, parent, level, acc_type) in enumerate(DRE_ACCOUNTS, start=1):
        cur.execute(
            """
            INSERT INTO dre_accounts
            (account_code, account_name, parent_code, hierarchy_level, account_type, sort_order)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (code, name, parent, level, acc_type, idx),
        )

    _seed_dre_performance(cur)

    supplier_ids: dict[str, int] = {}
    for name, area in SUPPLIER_AREAS.items():
        dre_code = AREA_TO_DRE.get(area, "04.01.02")
        cur.execute(
            "INSERT INTO suppliers (name, area, dre_account_code) VALUES (?, ?, ?)",
            (name, area, dre_code),
        )
        supplier_ids[name] = cur.lastrowid

    for (area, month), amount in BUDGET_2026.items():
        cur.execute(
            """
            INSERT INTO budget_lines (area, dre_account_code, month, budget_amount)
            VALUES (?, ?, ?, ?)
            """,
            (area, AREA_TO_DRE.get(area), month, amount),
        )

    with csv_path.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    invoice_count = 0
    for row in rows:
        if row.get("status") != "sucesso":
            continue

        supplier_name = row.get("fornecedor") or "Fornecedor Demo"
        area = SUPPLIER_AREAS.get(supplier_name, "Comercial")
        if supplier_name not in supplier_ids:
            cur.execute(
                "INSERT INTO suppliers (name, cnpj, area, dre_account_code) VALUES (?, ?, ?, ?)",
                (supplier_name, row.get("cnpj_emitente"), area, AREA_TO_DRE.get(area)),
            )
            supplier_ids[supplier_name] = cur.lastrowid

        amount = parse_amount(row.get("valor_total")) or 0.0
        file_path = row.get("caminho_arquivo", "")
        month = _month_key_from_path(file_path) or "2026-01"

        cur.execute(
            """
            INSERT INTO invoices
            (supplier_id, issue_month, issue_date, nf_number, amount, status, file_path)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                supplier_ids[supplier_name],
                month,
                month + "-01",
                row.get("numero_nf"),
                amount,
                row.get("status"),
                file_path,
            ),
        )
        invoice_id = cur.lastrowid
        invoice_count += 1

        cur.execute(
            "SELECT id FROM budget_lines WHERE area = ? AND month = ?",
            (area, month),
        )
        budget_row = cur.fetchone()
        if budget_row:
            cur.execute(
                "INSERT INTO actuals (budget_line_id, invoice_id, amount) VALUES (?, ?, ?)",
                (budget_row[0], invoice_id, amount),
            )

        cur.execute(
            "INSERT INTO payment_tickets (invoice_id, opened_at, status) VALUES (?, ?, ?)",
            (invoice_id, row.get("data_processamento", ""), "pago"),
        )

    conn.commit()
    conn.close()
    print(f"Banco criado: {db_path} ({invoice_count} faturas + DRE gerencial sintética)")
    return db_path


if __name__ == "__main__":
    build_database()
