from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db
from app.models.school import School, Major
from app.schemas.school import SchoolItem, MajorItem

router = APIRouter(prefix="/school", tags=["学校"])


@router.get("/list", summary="学校列表", response_model=list[SchoolItem])
def list_schools(
    name: str = Query("", description="学校名称（模糊搜索）"),
    db: Session = Depends(get_db),
):
    """获取学校列表，支持按名称模糊搜索"""
    query = db.query(School)
    if name:
        query = query.filter(School.name.contains(name))
    return query.order_by(School.id).all()


@router.get("/{school_id}/majors", summary="专业列表", response_model=list[MajorItem])
def list_majors(
    school_id: int,
    db: Session = Depends(get_db),
):
    """获取指定学校下的专业列表"""
    return (
        db.query(Major)
        .filter(Major.school_id == school_id)
        .order_by(Major.id)
        .all()
    )
