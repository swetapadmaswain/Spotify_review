"""Optional bearer-token authentication for protected API routes."""
from typing import Optional

from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from config.settings import settings

security = HTTPBearer(auto_error=False)


def authenticate_user(token: str) -> bool:
    if not settings.api_auth_token:
        return True
    return token == settings.api_auth_token


async def require_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
) -> bool:
    if not settings.api_auth_token:
        return True
    if not credentials or not authenticate_user(credentials.credentials):
        raise HTTPException(status_code=401, detail="Invalid or missing credentials")
    return True
