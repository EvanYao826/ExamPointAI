try:
    from celery import Celery
    from app.core.config import settings

    celery_app = Celery(
        "exampoint",
        broker=settings.REDIS_URL,
        backend=settings.REDIS_URL,
    )

    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="Asia/Shanghai",
        enable_utc=True,
        task_track_started=True,
    )

    # 自动发现任务模块
    celery_app.autodiscover_tasks(["app.tasks"])

except ImportError:
    # celery 未安装时不影响使用
    celery_app = None
