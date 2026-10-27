
import logging
import secrets
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from src.security import VerifyToken
from src.config import settings
from src.mail.models import PrivyrWebhook
from src.mail.services import generate_lead_email, send_lead_notification

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)

router = APIRouter()


@router.post("/webhooks/privyr")
async def receive_privyr_webhook(
    payload: PrivyrWebhook,
     _: Annotated[None, Depends(VerifyToken)],
):
    logger.info(
        "Privyr webhook received | event_type=%s",
        payload.event_type,
    )
    if payload.event_type != "CLIENT_CREATED":
        return {
            "success": True,
            "event_type": payload.event_type,
            "message": "Event received; no email sent",
        }

    client = payload.client or {}
    client_name = client.get("name")
    client_notes = client.get("notes")
    client_email = client.get("email")

    if not isinstance(client_email, str) or not client_email.strip():
        raise HTTPException(status_code=422, detail="Client email is missing")

    if not isinstance(client_notes, str) or not client_notes.strip():
        raise HTTPException(status_code=422, detail="Client notes are missing")

    if not isinstance(client_name, str):
        client_name = None

    try:
        draft = await generate_lead_email(
            client_name=client_name,
            client_notes=client_notes,
        )
    except Exception as exc:
        logger.exception("Gemini email draft generation failed")
        raise HTTPException(
            status_code=502,
            detail="Email draft generation failed. Check server logs.",
        ) from exc

    try:
        notification = await send_lead_notification(
            recipient=settings.it_team_email,
            draft=draft,
            client_name=client_name,
            client_email=client_email,
        )
        result = notification["result"]
    except Exception as exc:
        logger.exception("IT team email sending failed")
        raise HTTPException(
            status_code=502,
            detail="Email generated, but IT team notification failed.",
        ) from exc

    logger.info("Privyr webhook processed successfully")

    return {
        "success": True,
        "event_type": payload.event_type,
        "recipient": settings.it_team_email,
        "subject": draft.subject,
        "body": notification["email_body"],
        "email_status": result.get("status", "sent"),
        "message": "AI-generated lead notification sent to the IT team",
    }

