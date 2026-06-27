from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.auth import router as auth_router
from app.api.v1.user import router as user_router
from app.api.v1.school import router as school_router
from app.api.v1.subject import router as subject_router
from app.api.v1.bank import router as bank_router
from app.api.v1.question import router as question_router
from app.api.v1.wrong import router as wrong_router
from app.api.v1.upload import router as upload_router
from app.api.v1.ranking import router as ranking_router
from app.api.v1.statistics import router as statistics_router

app = FastAPI(
    title="考点通 API",
    description="ExamPoint AI - 大学生智能题库系统",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")
app.include_router(school_router, prefix="/api/v1")
app.include_router(subject_router, prefix="/api/v1")
app.include_router(bank_router, prefix="/api/v1")
app.include_router(question_router, prefix="/api/v1")
app.include_router(wrong_router, prefix="/api/v1")
app.include_router(upload_router, prefix="/api/v1")
app.include_router(ranking_router, prefix="/api/v1")
app.include_router(statistics_router, prefix="/api/v1")


@app.get("/", tags=["健康检查"])
def root():
    return {"service": "ExamPoint AI", "version": "1.0.0", "status": "running"}


@app.get("/health", tags=["健康检查"])
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
