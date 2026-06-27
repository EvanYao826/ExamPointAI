from pydantic import BaseModel, Field


class UpdateProfileRequest(BaseModel):
    nickname: str | None = Field(None, max_length=50, description="昵称")
    avatar: str | None = Field(None, max_length=255, description="头像地址")
    school_name: str | None = Field(None, max_length=100, description="学校名称")
    major_name: str | None = Field(None, max_length=100, description="专业名称")


class UserInfoResponse(BaseModel):
    id: int
    phone: str | None = None
    nickname: str
    avatar: str
    school_name: str | None = None
    major_name: str | None = None

    class Config:
        from_attributes = True
