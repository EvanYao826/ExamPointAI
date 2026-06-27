from pydantic import BaseModel


class SubjectItem(BaseModel):
    id: int
    name: str
    icon: str
    sort: int
    source: int = 0

    class Config:
        from_attributes = True


class SetSubjectsRequest(BaseModel):
    subject_ids: list[int] = []
    subject_names: list[str] = []
