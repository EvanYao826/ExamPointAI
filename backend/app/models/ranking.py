from sqlalchemy import Column, BigInteger, Integer, Date
from app.core.database import Base


class UserStatistics(Base):
    __tablename__ = "user_statistics"

    user_id = Column(BigInteger, primary_key=True, comment="用户ID")
    total_count = Column(Integer, default=0, comment="累计做题数")
    total_correct = Column(Integer, default=0, comment="累计正确数")
    continue_days = Column(Integer, default=0, comment="连续学习天数")
    last_study_date = Column(Date, default=None, comment="最后学习日期")
