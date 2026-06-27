from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, get_current_user
from app.models.user import User
from app.models.question import Question, QuestionOption, UserAnswerRecord
from app.models.bank import QuestionBank
from app.schemas.question import WrongListItem, WrongCountResponse, QuestionResponse, OptionItem

router = APIRouter(prefix="/wrong", tags=["错题"])


@router.get("/list", summary="错题列表", response_model=list[WrongListItem])
def list_wrong(
    bank_id: int = Query(None, description="题库ID（可选）"),
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


@router.get("/by-bank", summary="错题按题库分组")
def wrong_by_bank(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """按题库分组返回错题数量和题库名"""
    from sqlalchemy import func

    rows = (
        db.query(
            Question.bank_id,
            QuestionBank.name.label("bank_name"),
            func.count(UserAnswerRecord.id).label("wrong_count"),
        )
        .join(Question, UserAnswerRecord.question_id == Question.id)
        .join(QuestionBank, Question.bank_id == QuestionBank.id)
        .filter(
            UserAnswerRecord.user_id == user.id,
            UserAnswerRecord.is_correct == 0,
        )
        .group_by(Question.bank_id, QuestionBank.name)
        .all()
    )

    return [
        {"bank_id": r.bank_id, "bank_name": r.bank_name, "wrong_count": r.wrong_count}
        for r in rows
    ]


@router.get("/questions", summary="题库错题列表", response_model=list[QuestionResponse])
def wrong_questions(
    bank_id: int = Query(..., description="题库ID"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取某题库的全部错题（含选项），用于错题重做"""
    # 先查出错题 ID
    wrong_ids = (
        db.query(UserAnswerRecord.question_id)
        .join(Question, UserAnswerRecord.question_id == Question.id)
        .filter(
            UserAnswerRecord.user_id == user.id,
            UserAnswerRecord.is_correct == 0,
            Question.bank_id == bank_id,
        )
        .all()
    )
    wrong_ids = [r[0] for r in wrong_ids]

    if not wrong_ids:
        return []

    # 加载题目+选项
    questions = (
        db.query(Question)
        .filter(Question.id.in_(wrong_ids))
        .order_by(Question.id)
        .all()
    )

    result = []
    for q in questions:
        options = (
            db.query(QuestionOption)
            .filter(QuestionOption.question_id == q.id)
            .order_by(QuestionOption.option_key)
            .all()
        )
        result.append(QuestionResponse(
            id=q.id,
            bank_id=q.bank_id,
            type=q.type,
            content=q.content,
            difficulty=q.difficulty,
            options=[OptionItem.model_validate(opt) for opt in options],
        ))

    return result
