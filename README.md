# 考点通（ExamPoint AI）

> 大学生自己的"驾考宝典" —— 将老师发放的 Word/PDF 题库，一键转换为可刷题、可统计、可复习的智能题库系统。

## 项目结构

```
ExamPoint-AI/
├── sql/            # 数据库初始化脚本
├── backend/        # FastAPI 后端服务
├── miniapp/        # 微信小程序
└── docker-compose.yml
```

## 快速启动

```bash
# 1. 启动服务
docker-compose up -d

# 2. 访问 API 文档
open http://localhost:8000/docs
```

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | FastAPI + SQLAlchemy + Celery |
| 数据库 | MySQL 8.0 + Redis 7 |
| 存储 | MinIO |
| 小程序 | 微信原生开发 |
| 部署 | Docker Compose |

## 开发进度

- [x] 项目框架搭建
- [ ] 后端核心接口
- [ ] 小程序页面开发
- [ ] 文档解析功能
- [ ] 管理后台
