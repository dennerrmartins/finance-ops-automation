"""Configurações do Finance Ops Automation."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent

OUTPUT_DIR = BASE_DIR / "output"
NOTAS_DIR = OUTPUT_DIR / "notas"
PLANILHAS_DIR = OUTPUT_DIR / "planilhas"
RELATORIOS_DIR = OUTPUT_DIR / "relatorios"
DEMO_INBOX_DIR = BASE_DIR / "demo" / "inbox"
DATABASE_DIR = BASE_DIR / "database"
DB_PATH = DATABASE_DIR / "finance_ops.db"

CREDENTIALS_DIR = BASE_DIR / "credentials"
CREDENTIALS_FILE = CREDENTIALS_DIR / "credentials.json"
TOKEN_FILE = CREDENTIALS_DIR / "token.json"
PROCESSED_IDS_FILE = BASE_DIR / "processed_ids.json"
REGISTRY_FILE = BASE_DIR / "nf_registry.json"
CSV_FILENAME = "invoices_audit.csv"

AREAS = ("Comercial", "Marketing", "Experiencia Familia")

# Gmail (modo produção — opcional)
GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
]
GMAIL_SEARCH_QUERY = os.getenv(
    "GMAIL_SEARCH_QUERY",
    'is:unread ("nota fiscal" OR "NF-e" OR nfe OR fatura OR boleto OR invoice)',
)
SCHEDULE_TIMES = [t.strip() for t in os.getenv("SCHEDULE_TIMES", "09:00,12:00").split(",")]
LABEL_PROCESSED = os.getenv("LABEL_PROCESSED", "BOT/NF_PROCESSADA")

VALID_ATTACHMENT_EXTENSIONS = {".pdf", ".xml", ".zip"}
