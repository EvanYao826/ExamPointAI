from sqlalchemy import Column, BigInteger, String, DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class User(Base):
    __tablename__ = "user"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    phone = Column(String(20), unique=True, nullable=True, comment="手机号")
    openid = Column(String(100), unique=True, nullable=True, comment="微信openid")
    nickname = Column(String(50), default="", comment="昵称")
    avatar = Column(String(255), default="", comment="头像地址")
    school_id = Column(BigInteger, nullable=True, comment="学校ID")
    major_id = Column(BigInteger, nullable=True, comment="专业ID")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
