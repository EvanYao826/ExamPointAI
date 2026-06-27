from sqlalchemy import Column, BigInteger, String, Integer, SmallInteger, DateTime, Index
from sqlalchemy.sql import func

from app.core.database import Base


class QuestionBank(Base):
    __tablename__ = "question_bank"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="题库ID")
    subject_id = Column(BigInteger, nullable=False, comment="所属科目ID")
    creator_id = Column(BigInteger, nullable=False, comment="创建用户ID")
    name = Column(String(100), nullable=False, comment="题库名称")
    visibility = Column(SmallInteger, default=0, comment="可见范围：0私有 1学校共享 2公共题库")
    question_count = Column(Integer, default=0, comment="题目数量")
    source_file = Column(String(255), default="", comment="原始文件地址")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")

    __table_args__ = (
        Index("idx_subject_id", "subject_id"),
        Index("idx_creator_id", "creator_id"),
        Index("idx_visibility", "visibility"),
    )
