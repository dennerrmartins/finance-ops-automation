"""Exportação CSV com trilha de auditoria."""

import csv
from datetime import datetime
from pathlib import Path

import config

CSV_HEADERS = [
    "data_processamento",
    "arquivo_origem",
    "fornecedor",
    "numero_nf",
    "valor_total",
    "cnpj_emitente",
    "caminho_arquivo",
    "status",
    "observacao",
]


def append_record(
    csv_path: Path,
    *,
    source_file: str,
    supplier: str,
    numero_nf: str,
    valor_total: str,
    cnpj_emitente: str,
    destination: str,
    status: str,
    observacao: str = "",
) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    is_new = not csv_path.exists()
    with csv_path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_HEADERS)
        if is_new:
            writer.writeheader()
        writer.writerow(
            {
                "data_processamento": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "arquivo_origem": source_file,
                "fornecedor": supplier,
                "numero_nf": numero_nf or "",
                "valor_total": valor_total or "",
                "cnpj_emitente": cnpj_emitente or "",
                "caminho_arquivo": destination,
                "status": status,
                "observacao": observacao,
            }
        )


def default_csv_path() -> Path:
    return config.PLANILHAS_DIR / config.CSV_FILENAME
