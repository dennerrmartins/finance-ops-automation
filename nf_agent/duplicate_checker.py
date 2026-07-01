"""Controle de duplicidade de notas fiscais."""

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from loguru import logger

import config


@dataclass
class DuplicateResult:
    is_duplicate: bool
    reason: str
    existing_path: Optional[str] = None


class DuplicateChecker:
    def __init__(self, registry_path: Path = config.REGISTRY_FILE):
        self._path = registry_path
        raw = self._load()
        self._registry: dict[str, dict] = raw.get("nfs", raw) if isinstance(raw, dict) else {}
        self._hashes: dict[str, dict] = raw.get("hashes", {}) if isinstance(raw, dict) else {}

    def _load(self) -> dict:
        if self._path.exists():
            try:
                return json.loads(self._path.read_text(encoding="utf-8"))
            except Exception as exc:
                logger.warning(f"Registro inválido: {exc}")
        return {}

    def _save(self) -> None:
        data = {"nfs": self._registry, "hashes": self._hashes}
        self._path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    @staticmethod
    def compute_hash(file_path: Path) -> str:
        digest = hashlib.md5()
        with open(file_path, "rb") as handle:
            for chunk in iter(lambda: handle.read(8192), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def check_hash(self, file_hash: str) -> Optional[dict]:
        return self._hashes.get(file_hash)

    def register_hash(self, file_hash: str, file_path: str) -> None:
        self._hashes[file_hash] = {"caminho": file_path}
        self._save()

    def check(self, nf_data) -> DuplicateResult:
        for key in _build_keys(nf_data):
            if key in self._registry:
                entry = self._registry[key]
                return DuplicateResult(
                    is_duplicate=True,
                    reason=f"NF já processada ({key})",
                    existing_path=entry.get("caminho"),
                )
        return DuplicateResult(is_duplicate=False, reason="")

    def register(self, nf_data, file_path: str) -> None:
        entry = {
            "caminho": file_path,
            "cnpj": nf_data.cnpj_emitente or "",
            "numero_nf": nf_data.numero_nf or "",
            "valor_total": nf_data.valor_total or "",
        }
        for key in _build_keys(nf_data):
            self._registry[key] = entry
        self._save()


def _build_keys(nf_data) -> list[str]:
    keys: list[str] = []
    chave = re.sub(r"\D", "", nf_data.chave_acesso or "")
    if len(chave) == 44:
        keys.append(f"chave:{chave}")
    cnpj = re.sub(r"\D", "", nf_data.cnpj_emitente or "")
    numero = re.sub(r"\D", "", nf_data.numero_nf or "").lstrip("0")
    if cnpj and numero:
        keys.append(f"cnpj_num:{cnpj}_{numero}")
    return keys
