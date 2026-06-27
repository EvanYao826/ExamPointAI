from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, get_current_user
from app.models.user import User
from app.models.bank import QuestionBank
from app.schemas.bank import BankItem

router = APIRouter(prefix="/bank", tags=["题库"])


@router.get("/public", summary="公共题库", response_model=list[BankItem])
def list_public_banks(db: Session = Depends(get_db)):
    """获取公共题库列表（visibility=2）"""
    return (
        db.query(QuestionBank)
        .filter(QuestionBank.visibility == 2)
        .order_by(QuestionBank.create_time.desc())
        .all()
    )


@router.get("/mine", summary="我的题库", response_model=list[BankItem])
def list_my_banks(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取当前用户创建的题库"""
    return (
        db.query(QuestionBank)
        .filter(QuestionBank.creator_id == user.id)
        .order_by(QuestionBank.create_time.desc())
        .all()
    )
