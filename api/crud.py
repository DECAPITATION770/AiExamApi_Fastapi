from datetime import datetime
from typing import Optional, Any
from . import models


async def create_script(
    name: str,
    status: models.ScriptStatus,
    max_used: int = 50
) -> models.Script:
    return await models.Script.create(
        name=name,
        status=status,
        max_used=max_used,
    )

async def get_script_by_name(name: str) -> Optional[models.Script]:
    return await models.Script.get_or_none(name=name)

async def update_script_fields(script: models.Script, **fields: Any) -> models.Script:
    await script.update_from_dict(fields)
    await script.save()
    return await models.Script.get(id=script.id)

async def update_answer_fields(answer: models.Answer, **fields: Any) -> models.Answer:
    await answer.update_from_dict(fields)
    await answer.save()
    return await models.Answer.get(id=answer.id)

async def change_status(script: models.Script, status: models.ScriptStatus) -> models.Script:
    return await update_script_fields(script, status=status)

async def change_first_seen(script: models.Script, first_seen=datetime.now()) -> models.Script:
    if not script.first_seen:
        return await update_script_fields(script, first_seen=first_seen)
    return script

async def change_fingerprint(script: models.Script, fingerprint: str) -> models.Script:
    if not script.fingerprint:
        return await update_script_fields(script, fingerprint=fingerprint)
    return script

async def change_used(script: models.Script, used: int = 1) -> models.Script:
    if not script.used:
        return await update_script_fields(script, used=script.used + used)
    return script


async def create_answer_for_script(script: models.Script, answer_path: str = None, output: str | None = None) -> models.Answer:
    return await models.Answer.create(script=script, answer_path=answer_path, output=output)

async def change_answer_output(answer: models.Answer, output: str) -> models.Answer:
    return await update_answer_fields(answer, output=output)

async def change_answer_path(answer: models.Answer, answer_path: str) -> models.Answer:
    return await update_answer_fields(answer, answer_path=answer_path)
