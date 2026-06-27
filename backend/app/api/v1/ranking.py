from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.ranking import RankingItem, RankingResponse
from app.core.redis import (
    get_daily_ranking,
    get_weekly_ranking,
    get_daily_user_rank,
    get_weekly_user_rank,
)

router = APIRouter(prefix="/ranking", tags=["排行榜"])


def _build_ranking(
    db: Session,
    raw: list[tuple[str, float]],
    my_rank: int | None,
    my_score: float,
) -> RankingResponse:
    """将 Redis 结果组装为排行榜响应"""
    if not raw:
        return RankingResponse(list=[], my_rank=my_rank, my_score=int(my_score))

    user_ids = [int(uid) for uid, _ in raw]
    users = {u.id: u for u in db.query(User).filter(User.id.in_(user_ids)).all()}

    items = []
    for rank, (uid, score) in enumerate(raw, start=1):
        u = users.get(int(uid))
        items.append(RankingItem(
            rank=rank,
            user_id=int(uid),
            nickname=u.nickname if u else "未知用户",
            avatar=u.avatar if u else "",
            score=int(score),
        ))

    return RankingResponse(list=items, my_rank=my_rank, my_score=int(my_score))


@router.get("/daily", summary="今日排行", response_model=RankingResponse)
def daily_ranking(
    subject_id: int = Query(..., description="科目ID"),
    limit: int = Query(10, ge=1, le=100, description="返回数量"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取今日排行榜 Top N + 我的排名"""
    raw = get_daily_ranking(subject_id, limit)
    my_rank, my_score = get_daily_user_rank(subject_id, user.id)
    return _build_ranking(db, raw, my_rank, my_score)


@router.get("/weekly", summary="本周排行", response_model=RankingResponse)
def weekly_ranking(
    subject_id: int = Query(..., description="科目ID"),
    limit: int = Query(10, ge=1, le=100, description="返回数量"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取本周排行榜 Top N + 我的排名"""
    raw = get_weekly_ranking(subject_id, limit)
    my_rank, my_score = get_weekly_user_rank(subject_id, user.id)
    return _build_ranking(db, raw, my_rank, my_score)
