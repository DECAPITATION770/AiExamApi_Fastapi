from pydantic import BaseModel


class AnswerOutput(BaseModel):
    text: str
