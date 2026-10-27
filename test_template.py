from src.mail.model import TemplateInput
from src.mail.helper import build_email


lead = TemplateInput(
    portfolio="MS",
    scenario="T1",
    name="Rahul Menon",
    email="rahul@example.com",
    source="Google Ads landing page",
    service_name="Company formation",
    requirement_reflection=(
        "We understand you are looking to set up a free zone "
        "company for a consultancy business, with residence "
        "visas for two partners."
    ),
)

try:
    email = build_email(lead)

    print("Subject:", email.subject)
    print("\nBody:\n", email.body)
    print("\nSelected scenario:", email.scenario)

except ValueError as exc:
    print("Configuration or validation error:", exc)