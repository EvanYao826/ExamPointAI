from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, get_current_user
from app.models.user import User
from app.models.subject import Subject, UserSubject
from app.schemas.subject import SubjectItem, SetSubjectsRequest

router = APIRouter(tags=["科目"])


@router.get("/subject/list", summary="科目列表", response_model=list[SubjectItem])
def list_subjects(db: Session = Depends(get_db)):
    """获取全部科目列表"""
    return db.query(Subject).order_by(Subject.sort).all()


@router.post("/user/subjects", summary="选择科目")
def set_subjects(
    req: SetSubjectsRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """设置用户科目（覆盖写入）"""
    # 先删除旧的
    db.query(UserSubject).filter(UserSubject.user_id == user.id).delete()
    # 插入新的
    for sid in req.subject_ids:
        db.add(UserSubject(user_id=user.id, subject_id=sid))
    db.commit()
    return {"code": 0, "msg": "科目设置成功"}
