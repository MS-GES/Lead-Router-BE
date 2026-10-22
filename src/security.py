import secrets
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.config import settings

security = HTTPBearer(auto_error=False)


async def VerifyToken(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(security),
    ],
) -> None:
    expected_token = settings.privyr_webhook_secret
    received_token = credentials.credentials if credentials else ""

    if not expected_token or not secrets.compare_digest(
        received_token,
        expected_token,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing webhook token",
            headers={"WWW-Authenticate": "Bearer"},
        )