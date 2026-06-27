"""Redis 工具层 — 排行榜操作封装"""

from datetime import date, timedelta

import redis

from app.core.config import settings

# Redis 客户端单例
_redis_client: redis.Redis | None = None


def get_redis() -> redis.Redis | None:
    """获取 Redis 客户端，连接失败返回 None"""
    global _redis_client
    if _redis_client is None:
        try:
            _redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            _redis_client.ping()
        except redis.ConnectionError:
            _redis_client = None
    return _redis_client


def _daily_key(subject_id: int, d: date | None = None) -> str:
    d = d or date.today()
    return f"ranking:daily:{subject_id}:{d.isoformat()}"


def _weekly_key(subject_id: int, d: date | None = None) -> str:
    d = d or date.today()
    iso = d.isocalendar()
    return f"ranking:weekly:{subject_id}:{iso.year}-W{iso.week:02d}"


def incr_score(subject_id: int, user_id: int, delta: int = 1) -> None:
    """排行榜分数 +delta（今日 + 本周同时累加）"""
    r = get_redis()
    if r is None:
        return
    try:
        pipe = r.pipeline()
        dk = _daily_key(subject_id)
        wk = _weekly_key(subject_id)
        pipe.zincrby(dk, delta, str(user_id))
        pipe.zincrby(wk, delta, str(user_id))
        pipe.expire(dk, 86400 * 2)   # 2 天过期
        pipe.expire(wk, 86400 * 8)   # 8 天过期
        pipe.execute()
    except redis.ConnectionError:
        pass


def get_top_n(key: str, limit: int = 10) -> list[tuple[str, float]]:
    """获取 sorted set 前 N 名 [(member, score), ...]"""
    r = get_redis()
    if r is None:
        return []
    try:
        return r.zrevrange(key, 0, limit - 1, withscores=True)
    except redis.ConnectionError:
        return []


def get_user_rank_and_score(key: str, user_id: int) -> tuple[int | None, float]:
    """获取用户排名（从 1 开始）和分数，不存在返回 (None, 0)"""
    r = get_redis()
    if r is None:
        return None, 0
    try:
        rank = r.zrevrank(key, str(user_id))
        score = r.zscore(key, str(user_id))
        if rank is None:
            return None, 0
        return rank + 1, score or 0
    except redis.ConnectionError:
        return None, 0


def get_daily_ranking(subject_id: int, limit: int = 10) -> list[tuple[str, float]]:
    return get_top_n(_daily_key(subject_id), limit)


def get_weekly_ranking(subject_id: int, limit: int = 10) -> list[tuple[str, float]]:
    return get_top_n(_weekly_key(subject_id), limit)


def get_daily_user_rank(subject_id: int, user_id: int) -> tuple[int | None, float]:
    return get_user_rank_and_score(_daily_key(subject_id), user_id)


def get_weekly_user_rank(subject_id: int, user_id: int) -> tuple[int | None, float]:
    return get_user_rank_and_score(_weekly_key(subject_id), user_id)


def get_all_daily_keys(d: date | None = None) -> list[str]:
    """获取某日所有科目排行 key（用于持久化）"""
    r = get_redis()
    if r is None:
        return []
    try:
        return r.keys(f"ranking:daily:*:{d or date.today()}")
    except redis.ConnectionError:
        return []
