from fastapi import Request, HTTPException, status
from core.configs import settings

async def auth_required(request: Request):
    auth = request.headers.get("Auth")
    tokens = settings.AUTH_TOKENS
    if not auth or auth not in tokens:
        raise HTTPException(status_code=500)
