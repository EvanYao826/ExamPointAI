from sqlalchemy import Column, BigInteger, String, Integer

from app.core.database import Base


class Subject(Base):
    __tablename__ = "subject"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="科目ID")
    name = Column(String(50), nullable=False, comment="科目名称")
    icon = Column(String(255), default="", comment="图标地址")
    sort = Column(Integer, default=0, comment="排序")
    source = Column(Integer, default=0, comment="来源：0管理员添加 1用户添加")


class UserSubject(Base):
    __tablename__ = "user_subject"

    user_id = Column(BigInteger, primary_key=True, comment="用户ID")
    subject_id = Column(BigInteger, primary_key=True, comment="科目ID")
