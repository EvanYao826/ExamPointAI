from sqlalchemy import Column, BigInteger, String, Text, SmallInteger, DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class Question(Base):
    __tablename__ = "question"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    bank_id = Column(BigInteger, nullable=False, index=True, comment="题库ID")
    type = Column(String(30), nullable=False, index=True, comment="题目类型")
    content = Column(Text, nullable=False, comment="题目内容")
    answer = Column(Text, default="", comment="标准答案")
    analysis = Column(Text, default="", comment="答案解析")
    difficulty = Column(SmallInteger, default=1, comment="难度等级")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")


class QuestionOption(Base):
    __tablename__ = "question_option"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    question_id = Column(BigInteger, nullable=False, index=True, comment="题目ID")
    option_key = Column(String(5), nullable=False, comment="选项标识")
    content = Column(Text, nullable=False, comment="选项内容")
    is_answer = Column(SmallInteger, default=0, comment="是否正确答案")


class UserAnswerRecord(Base):
    __tablename__ = "user_answer_record"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True, comment="用户ID")
    question_id = Column(BigInteger, nullable=False, index=True, comment="题目ID")
    user_answer = Column(Text, default="", comment="用户答案")
    is_correct = Column(SmallInteger, default=0, comment="是否正确")
    cost_time = Column(BigInteger, default=0, comment="耗时秒数")
    create_time = Column(DateTime, server_default=func.now(), comment="答题时间")
