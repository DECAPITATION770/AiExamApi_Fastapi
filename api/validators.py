from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, status, UploadFile
from . import models
from . import crud
from core.configs import settings
from .models import ScriptStatus


def base_script_found_validate(script: models.Script):
    if not script:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="script_not_found")

async def validate_used(script: models.Script):
    base_script_found_validate(script)
    if script.max_used is not None and script.used >= script.max_used:
        await crud.change_status(script, ScriptStatus.LIMIT)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="usage_limit_reached")

async def validate_first_seen(script: models.Script):
    base_script_found_validate(script)
    if not script.first_seen:
        return
    now = datetime.now(timezone.utc)
    limit_time = script.first_seen + timedelta(minutes=settings.SCRIPT_ACTIVE_TIME_MINUTES)
    if now > limit_time:
        await crud.change_status(script, ScriptStatus.EXPIRED)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="usage_time_expired")

def validate_fingerprint(script: models.Script, fingerprint: str):
    base_script_found_validate(script)
    if not script.fingerprint:
        return
    if fingerprint != script.fingerprint:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="fingerprint_mismatch")

def image_validator(image: UploadFile):
    filename = image.filename.lower()
    if not filename.endswith((".png", ".jpg", ".jpeg")):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="image_must_be_png_jpg_jpeg")
