from fastapi import HTTPException, Header

from src.config import settings


async def get_token_from_header(authorization: str = Header(...)):
    startswith = f"{settings.oauth_settings.current_token_type} "
    if not authorization.startswith(startswith):
        raise HTTPException(status_code=401, detail="Invalid authorization header.")
    return authorization[len(startswith):]
