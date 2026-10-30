import logging

from fastapi import APIRouter, BackgroundTasks, Depends, status

from src.mail.helper import send_bd_team_notification
from src.mail.models import PrivyrWebhook
from src.mail.services import process_privyr_lead
from src.security import VerifyToken

logger = logging.getLogger(__name__)

router = APIRouter()


async def handle_lead_in_background(payload: PrivyrWebhook) -> None:
    """Process the lead in the background without holding the webhook HTTP connection."""
    try:
        await process_privyr_lead(payload)
    except Exception as exc:
        logger.exception("Error processing Privyr lead in background task")
        try:
            client = payload.client
            await send_bd_team_notification(
                case="processing_error",
                lead_name=client.name if client else None,
                lead_email=client.email if client else None,
                lead_phone=client.phone_number if client else None,
                lead_notes=client.notes if client else None,
                lead_source=client.source if client else None,
                reason=f"Background processing error: {exc}",
            )
        except Exception:
            logger.exception("Failed to send emergency BD team notification from background task")


@router.post(
    "/webhooks/privyr",
    dependencies=[Depends(VerifyToken)],
    status_code=status.HTTP_200_OK,
)
async def receive_privyr_webhook(
    payload: PrivyrWebhook,
    background_tasks: BackgroundTasks,
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

    # Immediately close connection to Privyr by offloading processing to the background
    background_tasks.add_task(handle_lead_in_background, payload)

    return {
        "success": True,
        "event_type": payload.event_type,
        "message": "Webhook received; processing lead in background",
    }
