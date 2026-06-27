from pydantic import BaseModel


class RankingItem(BaseModel):
    rank: int
    user_id: int
    nickname: str
    avatar: str
    total_count: int
    accuracy: float


class RankingResponse(BaseModel):
    list: list[RankingItem]
    my_rank: int | None = None
    my_total_count: int = 0
    my_accuracy: float = 0.0


class StatisticsResponse(BaseModel):
    total_count: int = 0
    total_correct: int = 0
    total_accuracy: float = 0.0
    continue_days: int = 0
