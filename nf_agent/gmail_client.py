"""Cliente Gmail API (modo produção — requer credentials.json)."""

import base64
import json
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from loguru import logger

import config


class GmailClient:
    def __init__(self):
        self._service = None
        self._processed_ids: set[str] = self._load_processed_ids()

    def _authenticate(self) -> Credentials:
        creds: Optional[Credentials] = None
        if config.TOKEN_FILE.exists():
            creds = Credentials.from_authorized_user_file(
                str(config.TOKEN_FILE), config.GMAIL_SCOPES
            )

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not config.CREDENTIALS_FILE.exists():
                    raise FileNotFoundError(
                        f"credentials.json não encontrado em {config.CREDENTIALS_FILE}. "
                        "Veja docs/nf_agent_architecture.md"
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(config.CREDENTIALS_FILE), config.GMAIL_SCOPES
                )
                creds = flow.run_local_server(port=0)
            config.CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
            config.TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
        return creds

    def connect(self) -> None:
        self._service = build("gmail", "v1", credentials=self._authenticate())
        logger.info("Gmail API conectada.")

    def _load_processed_ids(self) -> set[str]:
        if config.PROCESSED_IDS_FILE.exists():
            try:
                return set(json.loads(config.PROCESSED_IDS_FILE.read_text(encoding="utf-8")))
            except Exception as exc:
                logger.warning(f"IDs processados inválidos: {exc}")
        return set()

    def _save_processed_ids(self) -> None:
        config.PROCESSED_IDS_FILE.write_text(
            json.dumps(sorted(self._processed_ids), indent=2), encoding="utf-8"
        )

    def mark_as_processed(self, message_id: str) -> None:
        self._processed_ids.add(message_id)
        self._save_processed_ids()

    def is_processed(self, message_id: str) -> bool:
        return message_id in self._processed_ids

    def list_messages(self, query: str | None = None) -> list[dict]:
        if not self._service:
            raise RuntimeError("Chame connect() antes de list_messages().")
        search_query = query or config.GMAIL_SEARCH_QUERY
        messages: list[dict] = []
        page_token = None
        try:
            while True:
                params = {"userId": "me", "q": search_query, "maxResults": 200}
                if page_token:
                    params["pageToken"] = page_token
                response = self._service.users().messages().list(**params).execute()
                messages.extend(response.get("messages", []))
                page_token = response.get("nextPageToken")
                if not page_token:
                    break
        except HttpError as exc:
            logger.error(f"Erro ao listar mensagens: {exc}")
        new_messages = [m for m in messages if not self.is_processed(m["id"])]
        logger.info(f"Gmail: {len(messages)} encontrados, {len(new_messages)} novos")
        return new_messages

    def get_message_detail(self, message_id: str) -> Optional[dict]:
        try:
            return (
                self._service.users()
                .messages()
                .get(userId="me", id=message_id, format="full")
                .execute()
            )
        except HttpError as exc:
            logger.error(f"Erro ao obter mensagem {message_id}: {exc}")
            return None

    def get_attachment_data(self, message_id: str, attachment_id: str) -> Optional[bytes]:
        try:
            attachment = (
                self._service.users()
                .messages()
                .attachments()
                .get(userId="me", messageId=message_id, id=attachment_id)
                .execute()
            )
            return base64.urlsafe_b64decode(attachment.get("data", "") + "==")
        except HttpError as exc:
            logger.error(f"Erro ao baixar anexo: {exc}")
            return None

    def apply_label(self, message_id: str, label_name: str) -> bool:
        if not self._service:
            return False
        try:
            labels = self._service.users().labels().list(userId="me").execute()
            label_id = None
            for item in labels.get("labels", []):
                if item["name"] == label_name:
                    label_id = item["id"]
                    break
            if not label_id:
                created = (
                    self._service.users()
                    .labels()
                    .create(
                        userId="me",
                        body={
                            "name": label_name,
                            "labelListVisibility": "labelShow",
                            "messageListVisibility": "show",
                        },
                    )
                    .execute()
                )
                label_id = created["id"]
            self._service.users().messages().modify(
                userId="me",
                id=message_id,
                body={"addLabelIds": [label_id]},
            ).execute()
            return True
        except HttpError as exc:
            logger.error(f"Erro ao aplicar label: {exc}")
            return False
