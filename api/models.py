from tortoise import fields, models
from enum import StrEnum


import uuid
class ScriptStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    LIMIT = "limit"
    EXPIRED = "expired"

class ScriptStatusForUsers(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class BaseModel(models.Model):
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        abstract = True

class Script(BaseModel):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=10, unique=True)

    status = fields.CharEnumField(
        enum_type=ScriptStatus,
        default=ScriptStatus.INACTIVE,
        max_length=255,
    )

    first_seen = fields.DatetimeField(null=True)

    max_used = fields.IntField(default=50)
    used = fields.IntField(default=0)
    fingerprint = fields.TextField(null=True)

    def __str__(self):
        return f"{self.id}:{self.name}"

    class Meta:
        table = "scripts"

class Answer(BaseModel):
    id = fields.IntField(primary_key=True)
    script = fields.ForeignKeyField("models.Script", related_name="answers")

    answer_path = fields.TextField()
    output = fields.TextField(null=True)

    answer_unique_id = fields.TextField(default=lambda: f"{uuid.uuid4()}{uuid.uuid4()}")

    def __str__(self):
        return f"{self.id}:{self.script.name}"

    class Meta:
        table = "answers"


