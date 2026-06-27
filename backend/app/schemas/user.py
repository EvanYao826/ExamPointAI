from pydantic import BaseModel, Field


class UpdateProfileRequest(BaseModel):
    nickname: str | None = Field(None, max_length=50, description="昵称")
    avatar: str | None = Field(None, max_length=255, description="头像地址")


class UserInfoResponse(BaseModel):
    id: int
    phone: str | None = None
    nickname: str
    avatar: str
    school_id: int | None = None
    major_id: int | None = None

    class Config:
        from_attributes = True
