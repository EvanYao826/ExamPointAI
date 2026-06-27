import os
import uuid
import threading

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, get_current_user
from app.core.config import settings
from app.models.user import User
from app.models.bank import QuestionBank
from app.models.upload import UploadTask

router = APIRouter(prefix="/upload", tags=["上传"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/file", summary="上传题库文件")
async def upload_file(
    file: UploadFile = File(...),
    subject_id: int = Form(...),
    bank_name: str = Form(""),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """上传 Word/PDF 文件，创建题库和上传任务记录，触发异步解析"""
    allowed = ('.doc', '.docx', '.pdf')
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed:
        raise HTTPException(status_code=400, detail="仅支持 Word/PDF 文件")

    content = await file.read()
    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="文件不能超过20MB")

    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(content)

    # 创建题库
    name = bank_name or file.filename.replace(ext, "")
    bank = QuestionBank(
        subject_id=subject_id,
        creator_id=user.id,
        name=name,
        visibility=0,
        question_count=0,
        source_file=filepath,
    )
    db.add(bank)
    db.commit()
    db.refresh(bank)

    # 创建上传任务
    task = UploadTask(
        user_id=user.id,
        subject_id=subject_id,
        file_url=filepath,
        bank_id=bank.id,
        status=0,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    # 触发解析任务
    if ext == '.docx':
        if settings.USE_CELERY:
            # 生产环境：Celery 异步
            from app.tasks.parse_task import parse_bank_file
            parse_bank_file.delay(task.id, filepath, bank.id)
        else:
            # 开发环境：后台线程
            from app.tasks.parse_task import parse_bank_file_sync
            thread = threading.Thread(
                target=parse_bank_file_sync,
                args=(task.id, filepath, bank.id),
            )
            thread.daemon = True
            thread.start()

    return {
        "code": 0,
        "msg": "上传成功" + ("，正在解析中" if ext == ".docx" else "（仅支持 .docx 解析）"),
        "data": {
            "task_id": task.id,
            "bank_id": bank.id,
            "bank_name": bank.name,
        },
    }


@router.get("/tasks", summary="上传任务列表")
def list_tasks(
    status: int = Query(None, description="状态筛选"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取用户的上传任务列表"""
    query = db.query(UploadTask).filter(UploadTask.user_id == user.id)

    if status is not None:
        query = query.filter(UploadTask.status == status)

    tasks = query.order_by(UploadTask.create_time.desc()).all()

    result = []
    for t in tasks:
        # 查询题库名称
        bank_name = ""
        if t.bank_id:
            bank = db.query(QuestionBank).filter(QuestionBank.id == t.bank_id).first()
            if bank:
                bank_name = bank.name

        result.append({
            "id": t.id,
            "task_id": t.id,
            "bank_id": t.bank_id,
            "bank_name": bank_name or "未知题库",
            "status": t.status,
            "success_count": t.success_count,
            "fail_count": t.fail_count,
            "error_msg": t.error_msg,
            "create_time": str(t.create_time) if t.create_time else "",
        })

    return result


@router.get("/task/{task_id}", summary="任务详情")
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取单个上传任务详情"""
    task = db.query(UploadTask).filter(
        UploadTask.id == task_id,
        UploadTask.user_id == user.id,
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    # 查询题库名称
    bank_name = ""
    if task.bank_id:
        bank = db.query(QuestionBank).filter(QuestionBank.id == task.bank_id).first()
        if bank:
            bank_name = bank.name

    return {
        "id": task.id,
        "task_id": task.id,
        "bank_id": task.bank_id,
        "bank_name": bank_name or "未知题库",
        "status": task.status,
        "success_count": task.success_count,
        "fail_count": task.fail_count,
        "error_msg": task.error_msg,
        "create_time": str(task.create_time) if task.create_time else "",
    }
