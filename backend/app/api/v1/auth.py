from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db
from app.core.config import settings
from app.core.security import create_access_token
from app.models.user import User
from app.schemas.auth import SmsLoginRequest, SmsSendRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["认证"])

# 开发阶段固定验证码
MOCK_CODE = "888888"


@router.post("/sms/send", summary="发送验证码")
def send_sms(req: SmsSendRequest):
    """
    发送短信验证码。开发阶段使用固定验证码 888888。
    """
    if settings.SMS_MOCK:
        return {"code": 0, "msg": "验证码已发送（开发模式：888888）"}

    # TODO: 接入真实短信服务
    return {"code": 0, "msg": "验证码已发送"}


@router.post("/sms/login", summary="验证码登录", response_model=TokenResponse)
def sms_login(req: SmsLoginRequest, db: Session = Depends(get_db)):
    """
    手机号 + 验证码登录。未注册用户自动创建。
    """
    # 验证验证码
    expected_code = MOCK_CODE if settings.SMS_MOCK else ""
    if req.code != expected_code:
        raise HTTPException(status_code=400, detail="验证码错误")

    # 查找或创建用户
    user = db.query(User).filter(User.phone == req.phone).first()
    if user is None:
        user = User(phone=req.phone, nickname=f"用户{req.phone[-4:]}")
        db.add(user)
        db.commit()
        db.refresh(user)

    # 生成 token
    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token)
