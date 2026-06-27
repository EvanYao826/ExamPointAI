from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, get_current_user
from app.models.user import User
from app.models.question import Question, UserAnswerRecord
from app.schemas.question import WrongListItem, WrongCountResponse

router = APIRouter(prefix="/wrong", tags=["错题"])


@router.get("/list", summary="错题列表", response_model=list[WrongListItem])
def list_wrong(
    bank_id: int = Query(None, description="题库ID（可选，不传则返回全部错题）"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取错题列表，支持按题库筛选"""
    query = (
        db.query(
            UserAnswerRecord.question_id,
            Question.type,
            Question.content,
            UserAnswerRecord.user_answer,
            Question.answer.label("correct_answer"),
            Question.bank_id,
        )
        .join(Question, UserAnswerRecord.question_id == Question.id)
        .filter(
            UserAnswerRecord.user_id == user.id,
            UserAnswerRecord.is_correct == 0,
        )
    )

    if bank_id is not None:
        query = query.filter(Question.bank_id == bank_id)

    rows = query.order_by(UserAnswerRecord.create_time.desc()).all()

    return [
        WrongListItem(
            question_id=r.question_id,
            type=r.type,
            content=r.content,
            user_answer=r.user_answer,
            correct_answer=r.correct_answer,
            bank_id=r.bank_id,
        )
        for r in rows
    ]


@router.get("/count", summary="错题数量", response_model=WrongCountResponse)
def count_wrong(
    bank_id: int = Query(None, description="题库ID（可选）"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取错题总数"""
    query = (
        db.query(UserAnswerRecord)
        .join(Question, UserAnswerRecord.question_id == Question.id)
        .filter(
            UserAnswerRecord.user_id == user.id,
            UserAnswerRecord.is_correct == 0,
        )
    )

    if bank_id is not None:
        query = query.filter(Question.bank_id == bank_id)

    count = query.count()
    return WrongCountResponse(count=count)
