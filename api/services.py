import random
from typing import Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from tortoise.exceptions import IntegrityError
from fastapi import HTTPException, status

from . import crud, models
from core.configs import settings
from .schemas import Script_Pydantic

async def generate_name() -> Optional[str]:
    choices = settings.NAME_CHOICES
    min_len = settings.MIN_SCRIPT_NAME_LENGTH
    max_len = settings.MAX_SCRIPT_NAME_LENGTH
    fallback_len = settings.IF_SCRIPT_NAME_EXISTS
    max_attempts = settings.REPEAT_SCRIPT_NAME_GENERATE

    length = min_len
    for _ in range(max_attempts):
        name = "".join(random.choice(choices) for _ in range(length))
        if await crud.get_script_by_name(name) is None:
            return name
        length = min(length + 1, max_len)

    fallback = "".join(random.choice(choices) for _ in range(fallback_len))
    if await crud.get_script_by_name(fallback) is None:
        return fallback

    return None

async def generate_script(name: Optional[str] = None, max_used: int = 50, status: Optional[str] = models.ScriptStatus.INACTIVE) -> dict:
    name = name or await generate_name()
    if not name:
        return {"ok": False, "error": "name_not_generated", "data": None}

    attempts = 3
    for _ in range(attempts):
        try:
            script = await crud.create_script(
                name=name,
                status=status,
                max_used=max_used,
            )
            script_p = await Script_Pydantic.from_tortoise_orm(script)
            return {"ok": True, "error": None, "data": script_p}
        except IntegrityError:
            # name = await generate_name()
            if not name:
                break
    return {"ok": False, "error": "name_conflict", "data": None}

async def change_status(name: str, status_value: models.ScriptStatus) -> dict:
    script = await crud.get_script_by_name(name)
    if not script:
        return {"ok": False, "error": "script_not_found", "data": None}
    updated = await crud.update_script_fields(script, status=status_value)
    script_p = await Script_Pydantic.from_tortoise_orm(updated)
    return {"ok": True, "error": None, "data": script_p}

async def change_first_seen(name: str, first_seen: datetime) -> dict:
    script = await crud.get_script_by_name(name)
    if not script:
        return {"ok": False, "error": "script_not_found", "data": None}
    if first_seen.tzinfo is None:
        first_seen = first_seen.replace(tzinfo=timezone.utc)
    updated = await crud.update_script_fields(script, first_seen=first_seen)
    script_p = await Script_Pydantic.from_tortoise_orm(updated)
    return {"ok": True, "error": None, "data": script_p}

async def change_fingerprint(name: str, fingerprint: str) -> dict:
    script = await crud.get_script_by_name(name)
    if not script:
        return {"ok": False, "error": "script_not_found", "data": None}
    updated = await crud.update_script_fields(script, fingerprint=fingerprint)
    script_p = await Script_Pydantic.from_tortoise_orm(updated)
    return {"ok": True, "error": None, "data": script_p}


async def get_script_by_name(name: str) -> dict:
    script = await crud.get_script_by_name(name)
    if not script:
        return {"ok": False, "error": "script_not_found", "data": None}

    current_time = datetime.now(timezone.utc)
    if script.max_used <= script.used:
        script.status = models.ScriptStatus.LIMIT
    elif script.first_seen and script.first_seen < current_time:
        script.status = models.ScriptStatus.EXPIRED
    else:
        script.status = models.ScriptStatus.ACTIVE
    await crud.update_script_fields(script, status=script.status)

    script_p = await Script_Pydantic.from_tortoise_orm(script)
    return {"ok": True, "error": None, "data": script_p}

async def change_status_for_users(name: str, status_value: models.ScriptStatusForUsers) -> dict:
    script = await crud.get_script_by_name(name)

    if not script:
        return {"ok": False, "error": "script_not_found", "data": None}

    if script.fingerprint:
        await crud.update_script_fields(script, status=models.ScriptStatus.EXPIRED)
        script_p = await Script_Pydantic.from_tortoise_orm(script)
        return {"ok": False, "error": "fingerprint_activated", "data": script_p}

    if script.first_seen and script.first_seen + timedelta(minutes=settings.SCRIPT_ACTIVE_TIME_MINUTES) < datetime.now(timezone.utc):
        await crud.update_script_fields(script, status=models.ScriptStatus.EXPIRED)
        script_p = await Script_Pydantic.from_tortoise_orm(script)
        return {"ok": False, "error": "expired", "data": script_p}

    if script.max_used <= script.used:
        await crud.update_script_fields(script, status=models.ScriptStatus.EXPIRED)
        script_p = await Script_Pydantic.from_tortoise_orm(script)
        return {"ok": False, "error": "limit", "data": script_p}

    updated = await crud.update_script_fields(script, status=status_value)
    script_p = await Script_Pydantic.from_tortoise_orm(updated)
    return {"ok": True, "error": None, "data": script_p}


async def check_change_status_for_users(name: str) -> dict:
    script = await crud.get_script_by_name(name)

    if not script:
        return {"ok": False, "error": "script_not_found", "data": None}

    if script.fingerprint:
        await crud.update_script_fields(script, status=models.ScriptStatus.EXPIRED)
        script_p = await Script_Pydantic.from_tortoise_orm(script)
        return {"ok": False, "error": "fingerprint_activated", "data": script_p}

    if script.first_seen and script.first_seen + timedelta(minutes=settings.SCRIPT_ACTIVE_TIME_MINUTES) < datetime.now(timezone.utc):
        await crud.update_script_fields(script, status=models.ScriptStatus.EXPIRED)
        script_p = await Script_Pydantic.from_tortoise_orm(script)
        return {"ok": False, "error": "expired", "data": script_p}

    if script.max_used <= script.used:
        await crud.update_script_fields(script, status=models.ScriptStatus.EXPIRED)
        script_p = await Script_Pydantic.from_tortoise_orm(script)
        return {"ok": False, "error": "limit", "data": script_p}

    script_p = await Script_Pydantic.from_tortoise_orm(script)
    return {"ok": True, "error": None, "data": script_p}