import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, get_current_user
from app.models.user import User
from app.models.bank import QuestionBank

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
    """上传 Word/PDF 文件，创建题库和上传任务记录"""
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
    db.execute(
        text("INSERT INTO upload_task (user_id, subject_id, file_url, bank_id, status) VALUES (:uid, :sid, :fid, :bid, 0)"),
        {"uid": user.id, "sid": subject_id, "fid": filepath, "bid": bank.id},
    )
    db.commit()

    return {"code": 0, "msg": "上传成功", "data": {"bank_id": bank.id, "bank_name": bank.name}}


@router.get("/tasks", summary="上传任务列表")
def list_tasks(
    status: int = Query(None, description="状态筛选"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取用户的上传任务列表"""
    sql = """
        SELECT t.id, t.bank_id, COALESCE(b.name, '未知题库') AS bank_name,
               t.status, t.success_count, t.fail_count, t.create_time
        FROM upload_task t
        LEFT JOIN question_bank b ON t.bank_id = b.id
        WHERE t.user_id = :uid
    """
    params = {"uid": user.id}

    if status is not None:
        sql += " AND t.status = :status"
        params["status"] = status

    sql += " ORDER BY t.create_time DESC"

    rows = db.execute(text(sql), params).fetchall()

    return [
        {
            "id": r[0], "bank_id": r[1], "bank_name": r[2],
            "status": r[3], "success_count": r[4], "fail_count": r[5],
            "create_time": str(r[6]) if r[6] else "",
        }
        for r in rows
    ]
