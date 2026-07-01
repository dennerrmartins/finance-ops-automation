"""Organização padronizada de NF-e em biblioteca documental."""

import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from loguru import logger

import config
from nf_agent.extractor import NFData, extract_from_file


def organize_file(
    source_path: Path,
    fallback_date: datetime,
    nf_data: Optional[NFData] = None,
    copy: bool = True,
) -> dict:
    result = {"destination_path": None, "success": False, "error": None}
    try:
        nf_data = nf_data or extract_from_file(source_path)
        supplier = _supplier_name(nf_data, source_path.stem)
        file_date = _resolve_date(nf_data, source_path, fallback_date)
        dest_dir = config.NOTAS_DIR / supplier / file_date.strftime("%Y.%m.%d")
        dest_dir.mkdir(parents=True, exist_ok=True)
        filename = _build_filename(source_path, nf_data, file_date, supplier)
        dest_path = _unique_path(dest_dir / filename)

        if copy:
            shutil.copy2(str(source_path), str(dest_path))
        else:
            shutil.move(str(source_path), str(dest_path))

        result["destination_path"] = str(dest_path)
        result["success"] = True
        logger.info(f"Organizado: {source_path.name} -> {dest_path}")
    except Exception as exc:
        result["error"] = str(exc)
        logger.error(f"Falha ao organizar {source_path.name}: {exc}")
    return result


def _supplier_name(nf_data: NFData, filename_hint: str) -> str:
    if nf_data.razao_social_emitente:
        return _sanitize(nf_data.razao_social_emitente)
    if nf_data.cnpj_emitente:
        return f"CNPJ_{re.sub(r'\D', '', nf_data.cnpj_emitente)}"
    return _sanitize(filename_hint.replace("_", " "))[:40] or "Fornecedor Demo"


def _resolve_date(nf_data: NFData, source_path: Path, fallback: datetime) -> datetime:
    if nf_data.data_emissao:
        raw = nf_data.data_emissao.strip()[:10]
        for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
            try:
                return datetime.strptime(raw, fmt)
            except ValueError:
                continue
        if "T" in nf_data.data_emissao:
            try:
                return datetime.fromisoformat(nf_data.data_emissao[:19])
            except ValueError:
                pass
    match = re.search(r"(\d{4})\.(\d{2})\.(\d{2})", source_path.name)
    if match:
        y, m, d = map(int, match.groups())
        return datetime(y, m, d)
    return fallback


def _build_filename(source_path: Path, nf_data: NFData, file_date: datetime, supplier: str) -> str:
    ext = source_path.suffix.lower()
    short = re.sub(r"[^A-Za-z0-9_]", "", supplier.upper().replace(" ", "_"))[:24]
    date_str = file_date.strftime("%Y.%m.%d")
    prefix = f"{short}_{date_str}"
    if nf_data.numero_nf:
        numero = re.sub(r"\D", "", nf_data.numero_nf).lstrip("0") or nf_data.numero_nf
        return f"{prefix}_NF-{numero}{ext}"
    return f"{prefix}{ext}"


def _sanitize(name: str) -> str:
    for char in r'\/:*?"<>|':
        name = name.replace(char, " ")
    return re.sub(r"\s+", " ", name).strip()[:80] or "Fornecedor Demo"


def _unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    counter = 1
    while True:
        candidate = path.parent / f"{path.stem}_{counter}{path.suffix}"
        if not candidate.exists():
            return candidate
        counter += 1
