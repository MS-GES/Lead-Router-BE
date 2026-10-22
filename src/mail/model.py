from pydantic import BaseModel, ConfigDict, Field


class PrivyrWebhook(BaseModel):
    model_config = ConfigDict(extra="allow")

    event_type: str
    client: dict | None = None
    activity: dict | None = None


class EmailDraft(BaseModel):
    subject: str = Field(description="Email subject")
    body: str = Field(description="Complete plain-text email body")