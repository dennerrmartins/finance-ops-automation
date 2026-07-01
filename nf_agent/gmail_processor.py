"""Processador Gmail: anexos NF-e → biblioteca + CSV (modo produção)."""

import tempfile
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path

from loguru import logger

import config
from nf_agent.csv_export import append_record, default_csv_path
from nf_agent.duplicate_checker import DuplicateChecker
from nf_agent.extractor import extract_from_file
from nf_agent.gmail_client import GmailClient
from nf_agent.organizer import organize_file


def _walk_parts(parts: list, attachments: list) -> None:
    for part in parts or []:
        filename = part.get("filename") or ""
        body = part.get("body", {})
        if filename and body.get("attachmentId"):
            ext = Path(filename).suffix.lower()
            if ext in config.VALID_ATTACHMENT_EXTENSIONS:
                attachments.append(
                    {
                        "filename": filename,
                        "attachment_id": body["attachmentId"],
                    }
                )
        if part.get("parts"):
            _walk_parts(part["parts"], attachments)


def _extract_attachments(message: dict) -> list[dict]:
    attachments: list[dict] = []
    payload = message.get("payload", {})
    if payload.get("filename") and payload.get("body", {}).get("attachmentId"):
        attachments.append(
            {
                "filename": payload["filename"],
                "attachment_id": payload["body"]["attachmentId"],
            }
        )
    _walk_parts(payload.get("parts", []), attachments)
    return attachments


def _message_date(message: dict) -> datetime:
    headers = message.get("payload", {}).get("headers", [])
    for header in headers:
        if header.get("name", "").lower() == "date":
            try:
                return parsedate_to_datetime(header["value"])
            except Exception:
                break
    return datetime.now()


def process_gmail(
    gmail: GmailClient | None = None,
    csv_path: Path | None = None,
    query: str | None = None,
) -> dict:
    """Executa um ciclo Gmail → NF Agent."""
    csv_path = csv_path or default_csv_path()
    stats = {"emails": 0, "anexos": 0, "sucesso": 0, "duplicata": 0, "erro": 0}

    client = gmail or GmailClient()
    client.connect()

    config.NOTAS_DIR.mkdir(parents=True, exist_ok=True)
    config.PLANILHAS_DIR.mkdir(parents=True, exist_ok=True)
    dup = DuplicateChecker()

    messages = client.list_messages(query=query)
    stats["emails"] = len(messages)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        for item in messages:
            message_id = item["id"]
            detail = client.get_message_detail(message_id)
            if not detail:
                stats["erro"] += 1
                continue

            attachments = _extract_attachments(detail)
            if not attachments:
                client.mark_as_processed(message_id)
                continue

            email_date = _message_date(detail)
            processed_any = False

            for att in attachments:
                stats["anexos"] += 1
                data = client.get_attachment_data(message_id, att["attachment_id"])
                if not data:
                    stats["erro"] += 1
                    continue

                file_path = tmp_dir / att["filename"]
                file_path.write_bytes(data)

                nf_data = extract_from_file(file_path)
                file_hash = DuplicateChecker.compute_hash(file_path)
                if dup.check_hash(file_hash) or dup.check(nf_data).is_duplicate:
                    stats["duplicata"] += 1
                    append_record(
                        csv_path,
                        source_file=att["filename"],
                        supplier=nf_data.razao_social_emitente or "",
                        numero_nf=nf_data.numero_nf or "",
                        valor_total=nf_data.valor_total or "",
                        cnpj_emitente=nf_data.cnpj_emitente or "",
                        destination="",
                        status="duplicata",
                        observacao="NF já registrada",
                    )
                    continue

                organized = organize_file(
                    file_path,
                    fallback_date=email_date,
                    nf_data=nf_data,
                    copy=True,
                )
                if not organized["success"]:
                    stats["erro"] += 1
                    continue

                dest = organized["destination_path"]
                dup.register(nf_data, dest)
                dup.register_hash(file_hash, dest)
                stats["sucesso"] += 1
                processed_any = True
                append_record(
                    csv_path,
                    source_file=att["filename"],
                    supplier=nf_data.razao_social_emitente or "",
                    numero_nf=nf_data.numero_nf or "",
                    valor_total=nf_data.valor_total or "",
                    cnpj_emitente=nf_data.cnpj_emitente or "",
                    destination=dest,
                    status="sucesso",
                )

            if processed_any:
                client.apply_label(message_id, config.LABEL_PROCESSED)
            client.mark_as_processed(message_id)

    logger.info(
        f"NF Agent Gmail | emails={stats['emails']} anexos={stats['anexos']} "
        f"sucesso={stats['sucesso']} duplicata={stats['duplicata']} erro={stats['erro']}"
    )
    return stats
