"""
统计维护任务。

第八周后排行榜直接读取 user_statistics，不再使用 Redis ZSet 或
daily_ranking。这个任务用于从 user_answer_record 重算用户级统计，
方便联调或修复历史数据。
"""

from datetime import date, datetime, timedelta

from sqlalchemy import func

from app.core.database import SessionLocal
from app.models.question import UserAnswerRecord
from app.models.ranking import UserStatistics


def _to_date(value) -> date | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        return date.fromisoformat(value[:10])
    return None


def _count_continue_days(study_dates: list[date]) -> int:
    if not study_dates:
        return 0

    date_set = set(study_dates)
    current = max(date_set)
    count = 0
    while current in date_set:
        count += 1
        current -= timedelta(days=1)
    return count


def rebuild_user_statistics_sync() -> dict:
    """从最新答题记录重算 user_statistics。"""
    db = SessionLocal()
    try:
        rows = (
            db.query(
                UserAnswerRecord.user_id,
                func.count(UserAnswerRecord.id).label("total_count"),
                func.sum(UserAnswerRecord.is_correct).label("total_correct"),
                func.max(func.date(UserAnswerRecord.create_time)).label("last_study_date"),
            )
            .group_by(UserAnswerRecord.user_id)
            .all()
        )

        rebuilt = 0
        for row in rows:
            study_dates = [
                _to_date(item[0])
                for item in (
                    db.query(func.date(UserAnswerRecord.create_time))
                    .filter(UserAnswerRecord.user_id == row.user_id)
                    .distinct()
                    .all()
                )
            ]
            study_dates = [d for d in study_dates if d is not None]

            stats = (
                db.query(UserStatistics)
                .filter(UserStatistics.user_id == row.user_id)
                .first()
            )
            if stats is None:
                stats = UserStatistics(user_id=row.user_id)
                db.add(stats)

            stats.total_count = int(row.total_count or 0)
            stats.total_correct = int(row.total_correct or 0)
            stats.continue_days = _count_continue_days(study_dates)
            stats.last_study_date = _to_date(row.last_study_date)
            rebuilt += 1

        db.commit()
        return {"rebuilt": rebuilt}

    except Exception as exc:
        db.rollback()
        return {"error": str(exc)}

    finally:
        db.close()


try:
    from app.core.celery import celery_app

    if celery_app is not None:
        @celery_app.task(name="rebuild_user_statistics")
        def rebuild_user_statistics():
            return rebuild_user_statistics_sync()

except ImportError:
    pass
