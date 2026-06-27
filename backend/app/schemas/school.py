from pydantic import BaseModel


class SchoolItem(BaseModel):
    id: int
    name: str
    province: str
    city: str

    class Config:
        from_attributes = True


class MajorItem(BaseModel):
    id: int
    school_id: int
    name: str

    class Config:
        from_attributes = True
