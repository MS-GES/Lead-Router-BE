
from src.mail.models import LeadTestInput, PrivyrWebhook


def test_privyr_webhook_ignores_unused_fields():
    payload = PrivyrWebhook.model_validate({
        "event_type": "CLIENT_CREATED",
        "client": {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "assigned_to": {"name": "Jane Smith"},
            "custom_fields": [{"name": "Brand", "value": "MS"}],
        },
    })

    assert payload.client is not None
    assert payload.client.name == "John Doe"
    assert not hasattr(payload.client, "assigned_to")
    assert not hasattr(payload.client, "custom_fields")


def test_manual_lead_input():
    lead = LeadTestInput(
        portfolio="MS",
        name="John Doe",
        email="john.doe@example.com",
        selected_service="Company incorporation",
        message="I want to register a company in Dubai.",
    )

    assert lead.portfolio == "MS"
    assert lead.selected_service == "Company incorporation"
