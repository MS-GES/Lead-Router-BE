
# app/helper.py

import asyncio
import os
import smtplib
import ssl
from email.message import EmailMessage

from dotenv import load_dotenv

load_dotenv(override=True)

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"


def _send_email_sync(
    recipient: str,
    subject: str,
    body: str,
    sender_email: str | None = None,
) -> dict:
    if not all([SMTP_SERVER, SMTP_USERNAME, SMTP_PASSWORD]):
        raise RuntimeError("SMTP configuration is missing from .env")

    sender = sender_email or SMTP_USERNAME

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    msg.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
        server.ehlo()

        if SMTP_USE_TLS:
            server.starttls(context=context)
            server.ehlo()

        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)

    return {
        "status": "sent",
        "sender": sender,
        "recipient": recipient,
    }


async def send_email(
    recipient: str,
    subject: str,
    body: str,
    sender_email: str | None = None,
) -> dict:
    return await asyncio.to_thread(
        _send_email_sync,
        recipient,
        subject,
        body,
        sender_email,
    )
