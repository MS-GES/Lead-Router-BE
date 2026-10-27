from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    gemini_api_key: str
    gemini_model: str = "gemini-3.8-flash"
    gemini_fallback_model: str | None = None

    privyr_webhook_secret: str
    it_team_email: str
    company_name: str = "kitaab.ai"
    company_services: str = "Company incorporation and corporate advisory services"
    
    # SMTP configuration
    smtp_server: str
    smtp_port: int = 587
    smtp_username: str
    smtp_password: str
    smtp_use_tls: bool = True


    liquid_api_key: str
    liquid_model: str = "d1"


settings = Settings()
