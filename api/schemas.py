from datetime import datetime, timezone
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field
from pydantic.generics import GenericModel
from tortoise.contrib.pydantic import pydantic_model_creator

from . import models

Script_Pydantic = pydantic_model_creator(models.Script, name="Script")
ScriptSchema = Script_Pydantic

T = TypeVar("T")


class ResponseBase(GenericModel, Generic[T]):
    ok: bool = Field(..., description="Статус ответа")
    error: Optional[str] = Field(None, description="Код/сообщение ошибки, если есть")
    data: Optional[T] = Field(None, description="Полезная нагрузка ответа")


class ScriptResponse(ResponseBase[ScriptSchema]):
    ...

class EmptyResponse(ResponseBase[dict]):
    ...

class CreateScriptSchema(BaseModel):
    name: Optional[str] = Field(
        default=None,
        description="Script name (optional). Если не указан — сгенерируем."
    )
    max_used: Optional[int] = Field(
        default=50,
        ge=1,
        description="Max number of uses"
    )
    status: models.ScriptStatus = Field(
        default=models.ScriptStatus.INACTIVE,
        description="Новый статус скрипта"
    )


class ChangeScriptStatusSchema(BaseModel):
    status: models.ScriptStatus = Field(
        default=models.ScriptStatus.INACTIVE,
        description="Новый статус скрипта"
    )


class ChangeScriptFirstSeenSchema(BaseModel):
    first_seen: datetime = Field(
        ...,
        description="Время первого запуска. Допускается naive datetime — будет трактоваться как UTC.",
    )

class ChangeScriptFingerprintSchema(BaseModel):
    fingerprint: str = Field(..., min_length=1, description="Fingerprint скрипта")

class ChangeScriptStatusForUsersSchema(BaseModel):
    status: models.ScriptStatusForUsers = Field(
        ...,
        description="Статус скрипта для пользователей"
    )