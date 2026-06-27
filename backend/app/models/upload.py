from sqlalchemy import Column, BigInteger, String, Text, SmallInteger, DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class UploadTask(Base):
    __tablename__ = "upload_task"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="任务ID")
    user_id = Column(BigInteger, nullable=False, index=True, comment="上传用户")
    subject_id = Column(BigInteger, nullable=False, comment="所属科目")
    file_url = Column(String(255), nullable=False, comment="文件地址")
    bank_id = Column(BigInteger, default=None, comment="生成的题库ID")
    status = Column(SmallInteger, default=0, comment="任务状态：0等待 1解析中 2成功 3失败")
    success_count = Column(SmallInteger, default=0, comment="成功解析题数")
    fail_count = Column(SmallInteger, default=0, comment="失败题数")
    error_msg = Column(Text, default=None, comment="错误信息")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
