import logging

from fastapi import APIRouter, Depends, HTTPException

from src.mail.helper import send_bd_team_notification
from src.mail.models import PrivyrWebhook
from src.mail.services import process_privyr_lead
from src.security import VerifyToken

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/webhooks/privyr", dependencies=[Depends(VerifyToken)])
async def receive_privyr_webhook(payload: PrivyrWebhook):
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

    try:
        result = await process_privyr_lead(payload)
        return result
    except Exception as exc:
        logger.exception("Error processing Privyr lead in webhook router")
        try:
            client = payload.client
            await send_bd_team_notification(
                case="processing_error",
                lead_name=client.name if client else None,
                lead_email=client.email if client else None,
                lead_phone=client.phone_number if client else None,
                lead_notes=client.notes if client else None,
                lead_source=client.source if client else None,
                reason=f"Router error: {exc}",
            )
        except Exception:
            logger.exception("Failed to send emergency BD team notification from router")

        raise HTTPException(
            status_code=500,
            detail="Error processing Privyr lead. BD team has been alerted.",
        ) from exc
