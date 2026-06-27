from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, get_current_user
from app.models.user import User
from app.models.ranking import UserStatistics
from app.schemas.ranking import StatisticsResponse

router = APIRouter(prefix="/statistics", tags=["统计"])


@router.get("/overview", summary="学习统计", response_model=StatisticsResponse)
def statistics_overview(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取当前用户的学习统计"""
    stats = db.query(UserStatistics).filter(UserStatistics.user_id == user.id).first()

    if stats is None:
        return StatisticsResponse()

    return StatisticsResponse(
        total_count=stats.total_count,
        total_correct=stats.total_correct,
        total_accuracy=round(stats.total_correct / stats.total_count, 4) if stats.total_count > 0 else 0.0,
        continue_days=stats.continue_days,
    )
