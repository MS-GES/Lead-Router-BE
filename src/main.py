
import logging

from fastapi import FastAPI

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


@app.get("/")
async def health_check():
    return {
        "status": "ok",
        "service": "privyr-webhook",
    }
