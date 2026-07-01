"""Processador demo: simula caixa de entrada local -> biblioteca + CSV."""

from datetime import datetime
from pathlib import Path

from loguru import logger

import config
from nf_agent.csv_export import append_record, default_csv_path
from nf_agent.duplicate_checker import DuplicateChecker
from nf_agent.extractor import extract_from_file
from nf_agent.organizer import organize_file


def process_inbox(
    inbox_dir: Path = config.DEMO_INBOX_DIR,
    csv_path: Path | None = None,
    reset_output: bool = False,
) -> dict:
    csv_path = csv_path or default_csv_path()
    stats = {"total": 0, "sucesso": 0, "duplicata": 0, "erro": 0}

    if reset_output:
        if config.NOTAS_DIR.exists():
            for child in config.NOTAS_DIR.iterdir():
                if child.is_dir():
                    for f in child.rglob("*"):
                        if f.is_file():
                            f.unlink()
                elif child.is_file():
                    child.unlink()
        if csv_path.exists():
            csv_path.unlink()
        if config.REGISTRY_FILE.exists():
            config.REGISTRY_FILE.unlink()

    config.NOTAS_DIR.mkdir(parents=True, exist_ok=True)
    config.PLANILHAS_DIR.mkdir(parents=True, exist_ok=True)
    config.RELATORIOS_DIR.mkdir(parents=True, exist_ok=True)

    dup = DuplicateChecker()
    files = sorted(
        p for p in inbox_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in {".xml", ".pdf", ".zip"}
    )
    stats["total"] = len(files)
    logger.info(f"Processando {len(files)} arquivo(s) de {inbox_dir}")

    for file_path in files:
        try:
            nf_data = extract_from_file(file_path)
            file_hash = DuplicateChecker.compute_hash(file_path)
            hash_hit = dup.check_hash(file_hash)
            if hash_hit:
                stats["duplicata"] += 1
                append_record(
                    csv_path,
                    source_file=file_path.name,
                    supplier=nf_data.razao_social_emitente or "",
                    numero_nf=nf_data.numero_nf or "",
                    valor_total=nf_data.valor_total or "",
                    cnpj_emitente=nf_data.cnpj_emitente or "",
                    destination=hash_hit.get("caminho", ""),
                    status="duplicata",
                    observacao="Hash idêntico a arquivo já processado",
                )
                continue

            dup_result = dup.check(nf_data)
            if dup_result.is_duplicate:
                stats["duplicata"] += 1
                append_record(
                    csv_path,
                    source_file=file_path.name,
                    supplier=nf_data.razao_social_emitente or "",
                    numero_nf=nf_data.numero_nf or "",
                    valor_total=nf_data.valor_total or "",
                    cnpj_emitente=nf_data.cnpj_emitente or "",
                    destination=dup_result.existing_path or "",
                    status="duplicata",
                    observacao=dup_result.reason,
                )
                continue

            organized = organize_file(
                file_path,
                fallback_date=datetime.now(),
                nf_data=nf_data,
                copy=True,
            )
            if not organized["success"]:
                stats["erro"] += 1
                append_record(
                    csv_path,
                    source_file=file_path.name,
                    supplier=nf_data.razao_social_emitente or "",
                    numero_nf=nf_data.numero_nf or "",
                    valor_total=nf_data.valor_total or "",
                    cnpj_emitente=nf_data.cnpj_emitente or "",
                    destination="",
                    status="erro",
                    observacao=organized.get("error") or "Falha desconhecida",
                )
                continue

            dest = organized["destination_path"]
            dup.register(nf_data, dest)
            dup.register_hash(file_hash, dest)
            stats["sucesso"] += 1
            append_record(
                csv_path,
                source_file=file_path.name,
                supplier=nf_data.razao_social_emitente or "",
                numero_nf=nf_data.numero_nf or "",
                valor_total=nf_data.valor_total or "",
                cnpj_emitente=nf_data.cnpj_emitente or "",
                destination=dest,
                status="sucesso",
            )
        except Exception as exc:
            stats["erro"] += 1
            logger.exception(f"Erro em {file_path.name}: {exc}")

    _write_report(stats, csv_path)
    logger.info(
        f"Concluído | total={stats['total']} sucesso={stats['sucesso']} "
        f"duplicata={stats['duplicata']} erro={stats['erro']}"
    )
    return stats


def _write_report(stats: dict, csv_path: Path) -> None:
    report_path = config.RELATORIOS_DIR / f"relatorio_{datetime.now():%Y%m%d_%H%M%S}.txt"
    lines = [
        "NF Agent — Relatório de Processamento",
        "=" * 55,
        f"Total de arquivos: {stats['total']}",
        f"Sucesso: {stats['sucesso']}",
        f"Duplicatas: {stats['duplicata']}",
        f"Erros: {stats['erro']}",
        f"CSV: {csv_path}",
        f"Biblioteca: {config.NOTAS_DIR}",
    ]
    report_path.write_text("\n".join(lines), encoding="utf-8")
