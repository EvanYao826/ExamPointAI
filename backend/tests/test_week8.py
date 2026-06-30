"""第八周验收测试：用户级统计 + 排行榜。"""

import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.api.v1.question import _update_user_stats
from app.api.v1.ranking import _build_ranking
from app.api.v1.statistics import statistics_overview
from app.core.database import Base
from app.models.ranking import UserStatistics
from app.models.user import User


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_answer_statistics_updates_by_submit_count(db):
    _update_user_stats(db, user_id=1, delta_count=1, delta_correct=0)

    stats = db.query(UserStatistics).filter(UserStatistics.user_id == 1).first()
    assert stats.total_count == 1
    assert stats.total_correct == 0
    assert stats.continue_days == 1

    _update_user_stats(db, user_id=1, delta_count=1, delta_correct=1)

    db.refresh(stats)
    assert stats.total_count == 2
    assert stats.total_correct == 1


def test_ranking_orders_by_total_count_and_returns_current_user(db):
    db.add_all([
        User(id=1, nickname="第一名", avatar=""),
        User(id=2, nickname="当前用户", avatar=""),
        User(id=3, nickname="零刷题", avatar=""),
        UserStatistics(user_id=1, total_count=8, total_correct=6),
        UserStatistics(user_id=2, total_count=3, total_correct=2),
        UserStatistics(user_id=3, total_count=0, total_correct=0),
    ])
    db.commit()

    response = _build_ranking(db, current_user_id=2, limit=10)

    assert [item.user_id for item in response.list] == [1, 2]
    assert response.my_rank == 2
    assert response.my_total_count == 3
    assert response.my_accuracy == pytest.approx(0.6667)


def test_statistics_overview_returns_user_level_data(db):
    user = User(id=1, nickname="当前用户")
    db.add(user)
    db.add(UserStatistics(
        user_id=1,
        total_count=5,
        total_correct=4,
        continue_days=2,
    ))
    db.commit()

    response = statistics_overview(db=db, user=user)

    assert response.total_count == 5
    assert response.total_correct == 4
    assert response.total_accuracy == 0.8
    assert response.continue_days == 2
