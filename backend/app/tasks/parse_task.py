"""
文件解析任务（支持 Celery 和线程两种模式）
"""

from app.core.database import SessionLocal
from app.models.upload import UploadTask
from app.models.bank import QuestionBank
from app.models.question import Question, QuestionOption
from app.services.parser import parse_docx, parse_pdf


def _parse_and_save(task_id: int, filepath: str, bank_id: int) -> dict:
    """
    解析文件并入库（核心逻辑）

    Args:
        task_id: upload_task 记录 ID
        filepath: 文件路径
        bank_id: 题库 ID

    Returns:
        解析结果
    """
    db = SessionLocal()

    try:
        # 更新状态为解析中
        task = db.query(UploadTask).filter(UploadTask.id == task_id).first()
        if not task:
            return {"error": "任务不存在"}

        task.status = 1
        db.commit()

        # 解析文件
        if filepath.endswith('.docx'):
            questions_data = parse_docx(filepath)
        elif filepath.endswith('.pdf'):
            questions_data = parse_pdf(filepath)
        else:
            raise ValueError("仅支持 .docx 和 .pdf 格式")

        # 入库
        success_count = 0
        fail_count = 0

        for q_data in questions_data:
            try:
                # 创建题目
                question = Question(
                    bank_id=bank_id,
                    type=q_data["type"],
                    content=q_data["content"],
                    answer=q_data.get("answer", ""),
                    analysis=q_data.get("analysis", ""),
                    difficulty=1,
                )
                db.add(question)
                db.flush()  # 获取 question.id

                # 创建选项
                for opt in q_data.get("options", []):
                    option = QuestionOption(
                        question_id=question.id,
                        option_key=opt["key"],
                        content=opt["content"],
                        is_answer=opt.get("is_answer", 0),
                    )
                    db.add(option)

                success_count += 1
            except Exception:
                fail_count += 1
                continue

        # 更新题库题目数量
        bank = db.query(QuestionBank).filter(QuestionBank.id == bank_id).first()
        if bank:
            bank.question_count = success_count

        # 更新任务状态
        task.success_count = success_count
        task.fail_count = fail_count
        task.status = 2  # 成功
        db.commit()

        return {
            "task_id": task_id,
            "success_count": success_count,
            "fail_count": fail_count,
        }

    except Exception as e:
        # 更新任务状态为失败
        task = db.query(UploadTask).filter(UploadTask.id == task_id).first()
        if task:
            task.status = 3  # 失败
            task.error_msg = str(e)[:500]
            db.commit()

        return {"error": str(e)}

    finally:
        db.close()


# 同步版本（用于线程模式）
def parse_bank_file_sync(task_id: int, filepath: str, bank_id: int):
    """线程模式调用此函数"""
    return _parse_and_save(task_id, filepath, bank_id)


# Celery 版本（用于 Celery 模式）
try:
    from app.core.celery import celery_app

    if celery_app is not None:
        @celery_app.task(name="parse_bank_file", bind=True)
        def parse_bank_file(self, task_id: int, filepath: str, bank_id: int):
            """Celery 模式调用此函数"""
            return _parse_and_save(task_id, filepath, bank_id)

except ImportError:
    # Celery 未安装时不影响使用
    pass
