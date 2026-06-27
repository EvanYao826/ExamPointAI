from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, get_current_user
from app.models.user import User
from app.models.bank import QuestionBank
from app.models.question import Question, QuestionOption
from app.schemas.bank import BankItem, BankDetailResponse
from app.schemas.question import QuestionResponse, OptionItem

router = APIRouter(prefix="/bank", tags=["题库"])


@router.get("/public", summary="公共题库", response_model=list[BankItem])
def list_public_banks(
    subject_id: int = Query(None, description="科目ID（可选）"),
    db: Session = Depends(get_db),
):
    """获取公共题库列表（visibility=2），支持按科目筛选"""
    query = db.query(QuestionBank).filter(QuestionBank.visibility == 2)
    if subject_id is not None:
        query = query.filter(QuestionBank.subject_id == subject_id)
    return query.order_by(QuestionBank.create_time.desc()).all()


@router.get("/mine", summary="我的题库", response_model=list[BankItem])
def list_my_banks(
    subject_id: int = Query(None, description="科目ID（可选）"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取当前用户创建的题库，支持按科目筛选"""
    query = db.query(QuestionBank).filter(QuestionBank.creator_id == user.id)
    if subject_id is not None:
        query = query.filter(QuestionBank.subject_id == subject_id)
    return query.order_by(QuestionBank.create_time.desc()).all()


@router.get("/{bank_id}", summary="题库详情", response_model=BankDetailResponse)
def get_bank_detail(
    bank_id: int,
    db: Session = Depends(get_db),
):
    """获取题库详情"""
    bank = db.query(QuestionBank).filter(QuestionBank.id == bank_id).first()
    if bank is None:
        raise HTTPException(status_code=404, detail="题库不存在")
    return bank


@router.get("/{bank_id}/questions", summary="题库全部题目", response_model=list[QuestionResponse])
def get_bank_questions(
    bank_id: int,
    db: Session = Depends(get_db),
):
    """一次性获取题库全部题目（含选项），用于前端整卷加载"""
    questions = (
        db.query(Question)
        .filter(Question.bank_id == bank_id)
        .order_by(Question.id)
        .all()
    )

    result = []
    for q in questions:
        options = (
            db.query(QuestionOption)
            .filter(QuestionOption.question_id == q.id)
            .order_by(QuestionOption.option_key)
            .all()
        )
        result.append(QuestionResponse(
            id=q.id,
            bank_id=q.bank_id,
            type=q.type,
            content=q.content,
            difficulty=q.difficulty,
            options=[OptionItem.model_validate(opt) for opt in options],
        ))

    return result
