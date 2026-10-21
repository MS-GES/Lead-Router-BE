
# app/services/gmail_sender.py

import asyncio
import base64
from email.message import EmailMessage
from pathlib import Path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

BASE_DIR = Path(__file__).resolve().parent.parent
TOKEN_FILE = BASE_DIR / "token.json"
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

print("Gmail helper file:", Path(__file__).resolve())
print("Token path:", TOKEN_FILE)
print("Token exists:", TOKEN_FILE.exists())
def _send_email_sync(
    recipient: str,
    subject: str,
    body: str,
) -> dict:
    if not TOKEN_FILE.exists():
        raise RuntimeError(
            "Gmail is not authorized. Run authorize_gmail.py first."
        )

    credentials = Credentials.from_authorized_user_file(
        str(TOKEN_FILE), SCOPES
    )

    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        TOKEN_FILE.write_text(credentials.to_json(), encoding="utf-8")

    if not credentials.valid:
        raise RuntimeError(
            "Gmail authorization is invalid. Reauthorize Gmail."
        )

    message = EmailMessage()
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    encoded_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode("utf-8")

    service = build(
        "gmail",
        "v1",
        credentials=credentials,
        cache_discovery=False,
    )

    result = service.users().messages().send(
        userId="me",
        body={"raw": encoded_message},
    ).execute()

    return {"message_id": result["id"], "status": "sent"}


async def send_email(
    recipient: str,
    subject: str,
    body: str,
) -> dict:
    # Gmail's Python client is synchronous; keep it off the event loop.
    return await asyncio.to_thread(
        _send_email_sync,
        recipient,
        subject,
        body,
    )
