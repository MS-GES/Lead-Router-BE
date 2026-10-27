
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


Portfolio = Literal[
    "MS",
    "MS Kapital",
    "Dot&",
    "E7 Estates",
]

Scenario = Literal[
    "T1",
    "T2",
    "T3",
    "T4",
    "T5",
    "existing_client",
    "job_seeker",
    "no_email",
    "spam",
    "vendor",
    "manual_review",
]

ServiceFit = Literal[
    "supported",
    "unsupported",
    "unknown",
]

ExceptionCategory = Literal[
    "spam",
    "job_seeker",
    "existing_client",
    "vendor",
    "none",
    "manual_review",
]


class PrivyrClient(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str | None = None
    email: str | None = None
    phone_number: str | None = None
    notes: str | None = None
    created_at: float | None = None
    source: str | None = None


class PrivyrWebhook(BaseModel):
    model_config = ConfigDict(extra="ignore")

    event_type: str
    client: PrivyrClient | None = None
    activity: dict[str, Any] | None = None


class LeadTestInput(BaseModel):
    """Manual input for testing the workflow."""

    portfolio: Portfolio
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    source: str | None = None
    selected_service: str | None = None
    message: str | None = None
    qualification: dict[str, Any] = Field(
        default_factory=dict
    )


class TemplateDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenario: Scenario
    service_fit: ServiceFit = "unknown"
    identified_service: str | None = None
    reason: str | None = None


class RequirementReflection(BaseModel):
    reflection: str
    
class ExceptionScreeningResult(BaseModel):
    category: ExceptionCategory
    reason: str = Field(
        description="Brief reason based on the lead's information"
    )
    identified_service: str | None = Field(
        default=None,
        description="Service the lead appears to need, if identifiable"
    )
    service_reason: str | None = Field(
        default=None,
        description="Brief evidence supporting the service identification"
    )