from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, get_current_user
from app.models.user import User
from app.models.question import Question, QuestionOption, UserAnswerRecord
from app.schemas.question import (
    QuestionResponse, OptionItem,
    SubmitRequest, SubmitResponse,
    AnalysisResponse,
)

router = APIRouter(prefix="/question", tags=["题目"])


@router.get("/next", summary="获取下一题", response_model=QuestionResponse)
def get_next_question(
    bank_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取题库中用户尚未作答的下一题"""
    answered_ids = (
        db.query(UserAnswerRecord.question_id)
        .filter(UserAnswerRecord.user_id == user.id)
        .subquery()
    )

    question = (
        db.query(Question)
        .filter(Question.bank_id == bank_id, ~Question.id.in_(answered_ids))
        .order_by(Question.id)
        .first()
    )

    if question is None:
        raise HTTPException(status_code=404, detail="该题库已全部刷完")

    options = (
        db.query(QuestionOption)
        .filter(QuestionOption.question_id == question.id)
        .order_by(QuestionOption.option_key)
        .all()
    )

    return QuestionResponse(
        id=question.id,
        bank_id=question.bank_id,
        type=question.type,
        content=question.content,
        difficulty=question.difficulty,
        options=[OptionItem.model_validate(opt) for opt in options],
    )


@router.post("/submit", summary="提交答案", response_model=SubmitResponse)
def submit_answer(
    req: SubmitRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """提交用户答案，返回是否正确及解析"""
    question = db.query(Question).filter(Question.id == req.question_id).first()
    if question is None:
        raise HTTPException(status_code=404, detail="题目不存在")

    is_correct = req.user_answer.strip().upper() == question.answer.strip().upper()

    record = (
        db.query(UserAnswerRecord)
        .filter(
            UserAnswerRecord.user_id == user.id,
            UserAnswerRecord.question_id == req.question_id,
        )
        .first()
    )

    if record:
        record.user_answer = req.user_answer
        record.is_correct = 1 if is_correct else 0
        record.cost_time = req.cost_time
    else:
        record = UserAnswerRecord(
            user_id=user.id,
            question_id=req.question_id,
            user_answer=req.user_answer,
            is_correct=1 if is_correct else 0,
            cost_time=req.cost_time,
        )
        db.add(record)

    db.commit()

    return SubmitResponse(
        is_correct=is_correct,
        correct_answer=question.answer,
        analysis=question.analysis,
    )


@router.get("/{question_id}/analysis", summary="获取解析", response_model=AnalysisResponse)
def get_analysis(
    question_id: int,
    db: Session = Depends(get_db),
):
    """获取题目解析"""
    question = db.query(Question).filter(Question.id == question_id).first()
    if question is None:
        raise HTTPException(status_code=404, detail="题目不存在")

    options = (
        db.query(QuestionOption)
        .filter(QuestionOption.question_id == question.id)
        .order_by(QuestionOption.option_key)
        .all()
    )

    return AnalysisResponse(
        id=question.id,
        type=question.type,
        content=question.content,
        answer=question.answer,
        analysis=question.analysis,
        difficulty=question.difficulty,
        options=[OptionItem.model_validate(opt) for opt in options],
    )
