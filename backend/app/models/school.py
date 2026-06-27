from sqlalchemy import Column, BigInteger, String, Index

from app.core.database import Base


class School(Base):
    __tablename__ = "school"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="学校ID")
    name = Column(String(100), unique=True, nullable=False, comment="学校名称")
    province = Column(String(50), default="", comment="省份")
    city = Column(String(50), default="", comment="城市")


class Major(Base):
    __tablename__ = "major"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="专业ID")
    school_id = Column(BigInteger, nullable=False, comment="学校ID")
    name = Column(String(100), nullable=False, comment="专业名称")

    __table_args__ = (
        Index("idx_school_id", "school_id"),
    )
