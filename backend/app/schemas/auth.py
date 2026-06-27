from pydantic import BaseModel, Field


class SmsLoginRequest(BaseModel):
    phone: str = Field(..., min_length=11, max_length=11, description="手机号")
    code: str = Field(..., min_length=6, max_length=6, description="验证码")


class SmsSendRequest(BaseModel):
    phone: str = Field(..., min_length=11, max_length=11, description="手机号")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
