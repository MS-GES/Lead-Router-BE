
import asyncio
import logging
import smtplib
import ssl
from email.message import EmailMessage

from src.config import settings

logger = logging.getLogger(__name__)


def _send_email_sync(
    recipient: str,
    subject: str,
    body: str,
    sender_email: str | None = None,
) -> dict:
    sender = sender_email or settings.smtp_username

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    msg.set_content(body)

    context = ssl.create_default_context()

    try:
        with smtplib.SMTP(
            settings.smtp_server,
            settings.smtp_port,
            timeout=30,
        ) as server:
            server.ehlo()

            if settings.smtp_use_tls:
                server.starttls(context=context)
                server.ehlo()

            server.login(
                settings.smtp_username,
                settings.smtp_password,
            )

            server.send_message(msg)

        logger.info("Email sent successfully | recipient=%s", recipient)

        return {
            "status": "sent",
            "sender": sender,
            "recipient": recipient,
        }

    except (smtplib.SMTPException, OSError):
        logger.exception("SMTP email sending failed | recipient=%s", recipient)
        raise


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
