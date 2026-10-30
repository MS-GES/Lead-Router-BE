
import logging

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from src.mail.router import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

app = FastAPI(
    title="Privyr Webhook API",
    description="Receives Privyr events and sends personalized emails",
    version="1.0.0",
)

app.include_router(router)


@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    """Redirect root/base URL directly to interactive API documentation."""
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "privyr-webhook",
    }
