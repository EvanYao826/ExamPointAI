"""
排行榜持久化任务（支持 Celery 和线程两种模式）
每日凌晨执行，将昨日 Redis 排行榜数据同步到 MySQL
"""

from datetime import date, timedelta

from app.core.database import SessionLocal
from app.core.redis import get_redis
from app.models.ranking import DailyRanking


def _sync_daily_ranking(target_date: date | None = None) -> dict:
    """
    将指定日期的 Redis 排行榜持久化到 MySQL

    Args:
        target_date: 要同步的日期，默认为昨天

    Returns:
        同步结果
    """
    target_date = target_date or (date.today() - timedelta(days=1))
    db = SessionLocal()

    try:
        r = get_redis()
        if r is None:
            return {"error": "Redis 不可用"}

        # 查找目标日期的所有排行 key
        pattern = f"ranking:daily:*:{target_date.isoformat()}"
        keys = r.keys(pattern)

        if not keys:
            return {"date": target_date.isoformat(), "synced": 0}

        synced = 0
        for key in keys:
            # 解析 subject_id：ranking:daily:{subject_id}:{date}
            parts = key.split(":")
            if len(parts) != 4:
                continue
            try:
                subject_id = int(parts[2])
            except ValueError:
                continue

            # 读取排行数据
            members = r.zrevrange(key, 0, -1, withscores=True)
            for uid_str, score in members:
                try:
                    user_id = int(uid_str)
                except ValueError:
                    continue

                daily_count = int(score)

                # upsert
                record = (
                    db.query(DailyRanking)
                    .filter(
                        DailyRanking.user_id == user_id,
                        DailyRanking.subject_id == subject_id,
                        DailyRanking.study_date == target_date,
                    )
                    .first()
                )

                if record:
                    record.daily_count = daily_count
                else:
                    db.add(DailyRanking(
                        user_id=user_id,
                        subject_id=subject_id,
                        study_date=target_date,
                        daily_count=daily_count,
                    ))

                synced += 1

        db.commit()
        return {"date": target_date.isoformat(), "synced": synced}

    except Exception as e:
        db.rollback()
        return {"error": str(e)}

    finally:
        db.close()


# 同步版本（用于线程模式）
def sync_ranking_sync(target_date: date | None = None):
    """线程模式调用此函数"""
    return _sync_daily_ranking(target_date)


# Celery 版本
try:
    from app.core.celery import celery_app

    if celery_app is not None:
        @celery_app.task(name="sync_daily_ranking")
        def sync_daily_ranking(target_date_str: str | None = None):
            """Celery 模式调用此函数"""
            target_date = date.fromisoformat(target_date_str) if target_date_str else None
            return _sync_daily_ranking(target_date)

except ImportError:
    pass
