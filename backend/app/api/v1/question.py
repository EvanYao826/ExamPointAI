from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, get_current_user
from app.models.user import User
from app.models.bank import QuestionBank
from app.models.question import Question, QuestionOption, UserAnswerRecord
from app.models.ranking import UserStatistics
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

    # 记录是否为新答题（用于统计更新）
    is_new_record = record.id is None

    db.commit()

    # --- 排行榜 + 统计更新 ---
    bank = db.query(QuestionBank).filter(QuestionBank.id == question.bank_id).first()
    if bank and is_new_record:
        _update_ranking_and_stats(db, user.id, bank.subject_id, is_correct)

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


def _update_ranking_and_stats(db: Session, user_id: int, subject_id: int, is_correct: bool) -> None:
    """答题后更新 Redis 排行榜 + MySQL 用户统计"""
    # 1. Redis 排行榜
    try:
        from app.core.redis import incr_score
        incr_score(subject_id, user_id)
    except Exception:
        pass  # Redis 不可用时不影响主流程

    # 2. MySQL 用户统计
    today = date.today()
    stats = (
        db.query(UserStatistics)
        .filter(UserStatistics.user_id == user_id, UserStatistics.subject_id == subject_id)
        .first()
    )

    if stats is None:
        stats = UserStatistics(
            user_id=user_id,
            subject_id=subject_id,
            today_count=0,
            today_correct=0,
            week_count=0,
            total_count=0,
            total_correct=0,
            continue_days=0,
            last_study_date=None,
        )
        db.add(stats)

    # 日期边界处理
    if stats.last_study_date != today:
        stats.today_count = 0
        stats.today_correct = 0

        # 连续天数：昨天则 +1，否则重置
        if stats.last_study_date == today - timedelta(days=1):
            stats.continue_days += 1
        else:
            stats.continue_days = 1

    # 周边界处理
    if stats.last_study_date is None or stats.last_study_date.isocalendar()[1] != today.isocalendar()[1]:
        stats.week_count = 0

    # 累加
    stats.today_count += 1
    stats.week_count += 1
    stats.total_count += 1
    if is_correct:
        stats.today_correct += 1
        stats.total_correct += 1
    stats.last_study_date = today

    db.commit()
