import requests as http_requests
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db
from app.core.config import settings
from app.core.security import create_access_token
from app.models.user import User
from app.models.subject import UserSubject
from app.schemas.auth import SmsLoginRequest, SmsSendRequest, TokenResponse, WxLoginRequest

router = APIRouter(prefix="/auth", tags=["认证"])

# 开发阶段固定验证码
MOCK_CODE = "888888"


@router.post("/sms/send", summary="发送验证码")
def send_sms(req: SmsSendRequest):
    """发送短信验证码。开发阶段使用固定验证码 888888。"""
    if settings.SMS_MOCK:
        return {"code": 0, "msg": "验证码已发送（开发模式：888888）"}
    # TODO: 接入真实短信服务
    return {"code": 0, "msg": "验证码已发送"}


@router.post("/sms/login", summary="验证码登录", response_model=TokenResponse)
def sms_login(req: SmsLoginRequest, db: Session = Depends(get_db)):
    """手机号 + 验证码登录。未注册用户自动创建。"""
    expected_code = MOCK_CODE if settings.SMS_MOCK else ""
    if req.code != expected_code:
        raise HTTPException(status_code=400, detail="验证码错误")

    user = db.query(User).filter(User.phone == req.phone).first()
    if user is None:
        user = User(phone=req.phone, nickname=f"用户{req.phone[-4:]}")
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    needs_profile = _check_needs_profile(db, user)
    return TokenResponse(access_token=token, needs_profile=needs_profile)


@router.post("/wx/login", summary="微信登录", response_model=TokenResponse)
def wx_login(req: WxLoginRequest, db: Session = Depends(get_db)):
    """
    微信小程序登录。
    1. 用 code 调用微信 jscode2session 接口获取 openid
    2. 根据 openid 查找或创建用户
    3. 返回 JWT token
    """
    # 调用微信接口换取 openid
    wx_url = "https://api.weixin.qq.com/sns/jscode2session"
    params = {
        "appid": settings.WX_APPID,
        "secret": settings.WX_SECRET,
        "js_code": req.code,
        "grant_type": "authorization_code",
    }

    try:
        resp = http_requests.get(wx_url, params=params, timeout=10)
        data = resp.json()
    except Exception:
        raise HTTPException(status_code=500, detail="微信服务异常")

    openid = data.get("openid")
    if not openid:
        errcode = data.get("errcode", -1)
        errmsg = data.get("errmsg", "未知错误")
        raise HTTPException(status_code=400, detail=f"微信登录失败: {errmsg} (code={errcode})")

    # 根据 openid 查找或创建用户
    user = db.query(User).filter(User.openid == openid).first()
    if user is None:
        user = User(openid=openid, nickname="微信用户")
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    needs_profile = _check_needs_profile(db, user)
    return TokenResponse(access_token=token, needs_profile=needs_profile)


def _check_needs_profile(db: Session, user: User) -> bool:
    """检查用户是否需要填写学校/专业/科目信息"""
    if not user.school_name:
        return True
    has_subject = db.query(UserSubject).filter(UserSubject.user_id == user.id).first()
    return has_subject is None
