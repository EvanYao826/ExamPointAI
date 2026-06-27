from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.user import UpdateProfileRequest, UserInfoResponse

router = APIRouter(prefix="/user", tags=["用户"])


@router.get("/profile", summary="获取用户信息", response_model=UserInfoResponse)
def get_profile(user: User = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return user


@router.put("/profile", summary="更新用户信息", response_model=UserInfoResponse)
def update_profile(
    req: UpdateProfileRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """更新当前用户的昵称和头像"""
    if req.nickname is not None:
        user.nickname = req.nickname
    if req.avatar is not None:
        user.avatar = req.avatar

    db.commit()
    db.refresh(user)
    return user
