from sqlalchemy import Column, BigInteger, String, Integer, Date, DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class UserStatistics(Base):
    __tablename__ = "user_statistics"

    user_id = Column(BigInteger, primary_key=True, comment="用户ID")
    subject_id = Column(BigInteger, primary_key=True, comment="科目ID")
    today_count = Column(Integer, default=0, comment="今日做题数")
    today_correct = Column(Integer, default=0, comment="今日正确数")
    week_count = Column(Integer, default=0, comment="本周做题数")
    total_count = Column(Integer, default=0, comment="累计做题数")
    total_correct = Column(Integer, default=0, comment="累计正确数")
    continue_days = Column(Integer, default=0, comment="连续学习天数")
    last_study_date = Column(Date, default=None, comment="最后学习日期")


class DailyRanking(Base):
    __tablename__ = "daily_ranking"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="记录ID")
    user_id = Column(BigInteger, nullable=False, comment="用户ID")
    subject_id = Column(BigInteger, nullable=False, comment="科目ID")
    study_date = Column(Date, nullable=False, comment="学习日期")
    daily_count = Column(Integer, default=0, comment="当日刷题数")
    daily_correct = Column(Integer, default=0, comment="当日正确数")
