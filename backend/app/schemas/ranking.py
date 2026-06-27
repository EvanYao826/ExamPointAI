from pydantic import BaseModel


class RankingItem(BaseModel):
    rank: int
    user_id: int
    nickname: str
    avatar: str
    score: int


class RankingResponse(BaseModel):
    list: list[RankingItem]
    my_rank: int | None = None
    my_score: int | None = None


class StatisticsResponse(BaseModel):
    today_count: int = 0
    today_correct: int = 0
    today_accuracy: float = 0.0
    week_count: int = 0
    total_count: int = 0
    total_correct: int = 0
    total_accuracy: float = 0.0
    continue_days: int = 0
