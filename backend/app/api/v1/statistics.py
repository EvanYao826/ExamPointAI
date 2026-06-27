from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, get_current_user
from app.models.user import User
from app.models.ranking import UserStatistics
from app.schemas.ranking import StatisticsResponse

router = APIRouter(prefix="/statistics", tags=["统计"])


@router.get("/overview", summary="学习统计", response_model=StatisticsResponse)
def statistics_overview(
    subject_id: int = Query(..., description="科目ID"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取用户某科目的学习统计概览"""
    stats = (
        db.query(UserStatistics)
        .filter(UserStatistics.user_id == user.id, UserStatistics.subject_id == subject_id)
        .first()
    )

    if stats is None:
        return StatisticsResponse()

    # 日期边界：跨天则今日数据归零
    today = date.today()
    today_count = stats.today_count if stats.last_study_date == today else 0
    today_correct = stats.today_correct if stats.last_study_date == today else 0

    return StatisticsResponse(
        today_count=today_count,
        today_correct=today_correct,
        today_accuracy=round(today_correct / today_count, 4) if today_count > 0 else 0.0,
        week_count=stats.week_count,
        total_count=stats.total_count,
        total_correct=stats.total_correct,
        total_accuracy=round(stats.total_correct / stats.total_count, 4) if stats.total_count > 0 else 0.0,
        continue_days=stats.continue_days,
    )
