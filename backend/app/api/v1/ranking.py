from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, get_current_user
from app.models.user import User
from app.models.ranking import UserStatistics
from app.schemas.ranking import RankingItem, RankingResponse

router = APIRouter(prefix="/ranking", tags=["排行榜"])


@router.get("/daily", summary="今日排行", response_model=RankingResponse)
def daily_ranking(
    limit: int = Query(10, ge=1, le=100, description="返回数量"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """按总刷题数排行（今日排行即总排行）"""
    return _build_ranking(db, user.id, limit)


@router.get("/weekly", summary="本周排行", response_model=RankingResponse)
def weekly_ranking(
    limit: int = Query(10, ge=1, le=100, description="返回数量"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """按总刷题数排行"""
    return _build_ranking(db, user.id, limit)


def _build_ranking(db: Session, current_user_id: int, limit: int) -> RankingResponse:
    """查询排行榜：按 total_count 降序"""
    rows = (
        db.query(UserStatistics, User)
        .join(User, UserStatistics.user_id == User.id)
        .filter(UserStatistics.total_count > 0)
        .order_by(UserStatistics.total_count.desc())
        .limit(limit)
        .all()
    )

    items = []
    for rank, (stats, u) in enumerate(rows, start=1):
        acc = round(stats.total_correct / stats.total_count, 4) if stats.total_count > 0 else 0.0
        items.append(RankingItem(
            rank=rank,
            user_id=u.id,
            nickname=u.nickname or "微信用户",
            avatar=u.avatar or "",
            total_count=stats.total_count,
            accuracy=acc,
        ))

    # 我的排名
    my_stats = db.query(UserStatistics).filter(UserStatistics.user_id == current_user_id).first()
    my_total = my_stats.total_count if my_stats else 0
    my_acc = round(my_stats.total_correct / my_stats.total_count, 4) if my_stats and my_stats.total_count > 0 else 0.0

    my_rank = None
    if my_total > 0:
        higher = db.query(UserStatistics).filter(UserStatistics.total_count > my_total).count()
        my_rank = higher + 1

    return RankingResponse(
        list=items,
        my_rank=my_rank,
        my_total_count=my_total,
        my_accuracy=my_acc,
    )
