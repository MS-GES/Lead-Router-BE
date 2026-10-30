import logging
from typing import Any

from src.config import settings
from src.mail.helper import (
    build_email,
    choose_template,
    extract_lead_details,
    generate_requirement_reflection,
    screen_lead_exception,
    send_bd_team_notification,
    send_lead_notification,
    validate_lead_email,
)
from src.mail.models import (
    LeadInput,
    Portfolio,
    PrivyrWebhook,
    TemplateDecision,
)
from src.mail.service_catalogue import get_service_fit

logger = logging.getLogger(__name__)


async def process_privyr_lead(
    payload: PrivyrWebhook | dict[str, Any],
    default_portfolio: Portfolio = "MS",
) -> dict[str, Any]:
    """
    Main lead processing service when receiving a lead from Privyr.

    Step 1: Initially validate the email using pure Python.
    If the email is missing, empty, or invalid, skip AI generation,
    assign scenario 'no_email' (send_email=False), log, and return.

    Step 2: If the email is valid, proceed with AI classification,
    template selection, reflection generation, and internal notification.
    """
    event_type = payload.event_type if isinstance(payload, PrivyrWebhook) else payload.get("event_type", "UNKNOWN")

    client_name = None
    raw_email = None
    client_notes = None
    portfolio = default_portfolio
    selected_service = None
    source = None
    phone = None
    cleaned_email = None
    is_valid = False
    created_at = None

    try:
        lead_info = extract_lead_details(payload, default_portfolio=default_portfolio)

        client_name = lead_info["name"]
        raw_email = lead_info["email"]
        client_notes = lead_info["notes"]
        portfolio = lead_info["portfolio"]
        selected_service = lead_info["selected_service"]
        source = lead_info["source"]
        phone = lead_info["phone"]
        created_at = lead_info.get("created_at")
        qualification = lead_info.get("qualification") or {}

        # ------------------------------------------------------------------
        # Step 1: Initial Python Email Validation
        # ------------------------------------------------------------------
        is_valid, cleaned_email, failure_reason = validate_lead_email(raw_email)

        if not is_valid:
            logger.info(
                "Lead email check failed | reason=%s | client_name=%s | email=%s",
                failure_reason,
                client_name,
                raw_email,
            )

            decision = TemplateDecision(
                scenario="no_email",
                service_fit="unknown",
                identified_service=selected_service,
                reason=f"Python email check: {failure_reason}",
            )

            # Notify the BD team via email with common format for 'no_email'
            bd_recipient = settings.bd_team_email or settings.it_team_email
            bd_status = "not_sent"
            bd_body = ""
            bd_subject = ""

            try:
                bd_notification = await send_bd_team_notification(
                    case="no_email",
                    lead_name=client_name,
                    lead_email=raw_email,
                    lead_phone=phone,
                    lead_notes=client_notes,
                    lead_source=source,
                    portfolio=portfolio,
                    selected_service=selected_service,
                    reason=failure_reason or "Email address is missing or empty",
                )
                bd_status = bd_notification.get("status", "sent")
                bd_body = bd_notification.get("email_body", "")
                bd_subject = bd_notification.get("subject", "")
            except Exception as exc:
                logger.exception("Failed to send BD team notification email for lead without email")
                bd_status = f"failed: {exc}"

            return {
                "success": True,
                "event_type": event_type,
                "scenario": "no_email",
                "email_valid": False,
                "send_email": False,
                "recipient": bd_recipient,
                "subject": bd_subject,
                "body": bd_body,
                "email_status": bd_status,
                "reason": failure_reason,
                "client_name": client_name,
                "client_email": raw_email,
                "created_at": created_at,
                "decision": decision.model_dump(),
                "message": f"Lead processed with scenario 'no_email' ({failure_reason}). Email sent to BD team.",
            }

        # ------------------------------------------------------------------
        # Step 2: Email is valid -> proceed with template selection & AI pipeline
        # ------------------------------------------------------------------
        logger.info(
            "Lead email check passed | email=%s | client_name=%s",
            cleaned_email,
            client_name,
        )

        lead_input = LeadInput(
            portfolio=portfolio,
            name=client_name,
            email=cleaned_email,
            phone=phone,
            source=source,
            created_at=created_at,
            selected_service=selected_service,
            message=client_notes,
            qualification=qualification,
        )

        # Check if message and qualification are both empty -> directly select T3 template
        is_message_empty = not (client_notes and client_notes.strip())
        is_qualification_empty = not qualification or not any(
            str(v).strip() for v in qualification.values() if v is not None
        )

        if is_message_empty and is_qualification_empty:
            logger.info(
                "Lead message and qualification are both empty | directly selecting T3 template | lead_name=%s",
                client_name,
            )
            service_fit = (
                get_service_fit(portfolio, selected_service)
                if selected_service
                else "unknown"
            )
            decision = TemplateDecision(
                scenario="T3",
                service_fit=service_fit,
                identified_service=selected_service,
                reason="Both message and qualification are empty; directly selected T3 template.",
            )
        else:
            # Otherwise, call screen_lead_exception first
            logger.info(
                "Screening lead for exceptions with Gemini | lead_name=%s",
                client_name,
            )
            screening_result = await screen_lead_exception(
                client_name=client_name,
                client_notes=client_notes,
                qualification=qualification,
            )

            logger.info(
                "Exception screening result | category=%s | reason=%s",
                screening_result.category,
                screening_result.reason,
            )

            if screening_result.category != "none":
                service_fit = (
                    get_service_fit(portfolio, selected_service)
                    if selected_service
                    else "unknown"
                )
                decision = TemplateDecision(
                    scenario=screening_result.category,
                    service_fit=service_fit,
                    identified_service=selected_service,
                    reason=screening_result.reason,
                )
            else:
                decision = await choose_template(lead=lead_input)

        # ------------------------------------------------------------------
        # Step 3: Handle Exception / Non-Standard Cases (manual_review, spam, etc.)
        # ------------------------------------------------------------------
        if decision.scenario in {
            "manual_review",
            "spam",
            "job_seeker",
            "existing_client",
            "vendor",
            "no_email",
        }:
            logger.info(
                "Lead exception detected by AI | scenario=%s | reason=%s",
                decision.scenario,
                decision.reason,
            )

            bd_recipient = settings.bd_team_email or settings.it_team_email
            bd_status = "not_sent"
            bd_body = ""
            bd_subject = ""

            try:
                bd_notification = await send_bd_team_notification(
                    case=decision.scenario,
                    lead_name=client_name,
                    lead_email=cleaned_email,
                    lead_phone=phone,
                    lead_notes=client_notes,
                    lead_source=source,
                    portfolio=portfolio,
                    selected_service=decision.identified_service or selected_service,
                    reason=decision.reason,
                )
                bd_status = bd_notification.get("status", "sent")
                bd_body = bd_notification.get("email_body", "")
                bd_subject = bd_notification.get("subject", "")
            except Exception as exc:
                logger.exception("Failed to send BD notification for exception lead: %s", decision.scenario)
                bd_status = f"failed: {exc}"

            return {
                "success": True,
                "event_type": event_type,
                "scenario": decision.scenario,
                "email_valid": True,
                "send_email": False,
                "recipient": bd_recipient,
                "subject": bd_subject,
                "body": bd_body,
                "email_status": bd_status,
                "decision": decision.model_dump(),
                "client_name": client_name,
                "client_email": cleaned_email,
                "created_at": created_at,
                "message": f"Lead classified as '{decision.scenario}'. Notification email sent to BD team.",
            }

        # ------------------------------------------------------------------
        # Step 4: Standard Leads (T1 - T5) -> Generate email & notify internal team
        # ------------------------------------------------------------------
        reflection = None
        if decision.scenario in {"T1", "T2"} and (client_notes or qualification):
            try:
                reflection = await generate_requirement_reflection(
                    portfolio=portfolio,
                    service=decision.identified_service,
                    message=client_notes,
                    qualification=qualification or {},
                )
            except Exception as exc:
                logger.warning(
                    "Gemini requirement reflection failed | error=%s | continuing with fallback",
                    exc,
                )
                reflection = None

        # Specification rule (Page 4): "If it can't be written cleanly, send T2 instead"
        # And Page 1: "If unsure between T2 and T3, use the shorter template"
        if decision.scenario == "T1" and not reflection:
            if decision.identified_service:
                logger.info(
                    "T1 reflection not available; falling back to T2 | service=%s",
                    decision.identified_service,
                )
                decision.scenario = "T2"
            else:
                logger.info(
                    "T1 reflection and identified service not available; falling back to T3"
                )
                decision.scenario = "T3"

        elif decision.scenario == "T2" and not decision.identified_service:
            logger.info("T2 identified service not available; falling back to T3")
            decision.scenario = "T3"

        email_content = build_email(
            lead=lead_input,
            decision=decision,
            requirement_reflection=reflection,
        )

        result_status = "not_sent"
        notification_body = email_content.body

        # If email should be sent and internal notification is needed
        if email_content.send_email and settings.it_team_email:
            try:
                notification = await send_lead_notification(
                    recipient=settings.it_team_email,
                    draft=email_content,
                    client_name=client_name,
                    client_email=cleaned_email,
                )
                result_status = notification.get("result", {}).get("status", "sent")
                notification_body = notification.get("email_body", email_content.body)
            except Exception as exc:
                logger.exception("Failed to send internal lead notification email")
                result_status = f"failed: {exc}"

        return {
            "success": True,
            "event_type": event_type,
            "scenario": decision.scenario,
            "email_valid": True,
            "send_email": email_content.send_email,
            "recipient": settings.it_team_email if email_content.send_email else None,
            "subject": email_content.subject,
            "body": notification_body,
            "email_status": result_status,
            "decision": decision.model_dump(),
            "client_name": client_name,
            "client_email": cleaned_email,
            "created_at": created_at,
            "message": (
                "Lead processed and notification dispatched"
                if email_content.send_email
                else f"Lead processed with scenario '{decision.scenario}'. No outgoing email required."
            ),
        }

    except Exception as exc:
        logger.exception("Lead processing failed unexpectedly | error=%s", exc)

        bd_recipient = settings.bd_team_email or settings.it_team_email
        bd_status = "not_sent"
        bd_body = ""
        bd_subject = ""

        try:
            bd_notification = await send_bd_team_notification(
                case="processing_error",
                lead_name=client_name,
                lead_email=cleaned_email or raw_email,
                lead_phone=phone,
                lead_notes=client_notes,
                lead_source=source,
                portfolio=portfolio,
                selected_service=selected_service,
                reason=f"Processing failed: {str(exc)}",
            )
            bd_status = bd_notification.get("status", "sent")
            bd_body = bd_notification.get("email_body", "")
            bd_subject = bd_notification.get("subject", "")
        except Exception as notify_exc:
            logger.exception("Failed to send BD notification for processing error: %s", notify_exc)
            bd_status = f"failed: {notify_exc}"

        return {
            "success": False,
            "event_type": event_type,
            "scenario": "processing_error",
            "email_valid": is_valid,
            "send_email": False,
            "recipient": bd_recipient,
            "subject": bd_subject,
            "body": bd_body,
            "email_status": bd_status,
            "error": str(exc),
            "client_name": client_name,
            "client_email": cleaned_email or raw_email,
            "created_at": created_at,
            "message": f"Lead processing encountered an error ({exc}). Alert email sent to BD team.",
        }
