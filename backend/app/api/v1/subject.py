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


@router.get("/user/subjects", summary="获取用户已选科目", response_model=list[SubjectItem])
def get_user_subjects(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取当前用户已选的科目列表"""
    subjects = (
        db.query(Subject)
        .join(UserSubject, UserSubject.subject_id == Subject.id)
        .filter(UserSubject.user_id == user.id)
        .order_by(Subject.sort)
        .all()
    )
    return subjects


@router.post("/user/subjects", summary="选择科目")
def set_subjects(
    req: SetSubjectsRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """设置用户科目（覆盖写入），支持传入已有ID和新科目名称"""
    # 先删除旧的
    db.query(UserSubject).filter(UserSubject.user_id == user.id).delete()

    # 处理已有科目 ID
    all_ids = list(req.subject_ids)

    # 处理新科目名称（创建并关联）
    for name in req.subject_names:
        name = name.strip()
        if not name:
            continue
        # 检查是否已存在
        existing = db.query(Subject).filter(Subject.name == name).first()
        if existing:
            if existing.id not in all_ids:
                all_ids.append(existing.id)
        else:
            # 创建新科目，source=1 表示用户添加
            new_subject = Subject(name=name, source=1)
            db.add(new_subject)
            db.flush()
            all_ids.append(new_subject.id)

    # 插入关联
    for sid in all_ids:
        db.add(UserSubject(user_id=user.id, subject_id=sid))
    db.commit()
    return {"code": 0, "msg": "科目设置成功"}
