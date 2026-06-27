from datetime import datetime

from pydantic import BaseModel


class BankItem(BaseModel):
    id: int
    subject_id: int
    name: str
    visibility: int
    question_count: int
    create_time: datetime | None

    class Config:
        from_attributes = True
