from pydantic import BaseModel


class SubjectItem(BaseModel):
    id: int
    name: str
    icon: str
    sort: int

    class Config:
        from_attributes = True


class SetSubjectsRequest(BaseModel):
    subject_ids: list[int]
