from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # MySQL
    DATABASE_URL: str = "mysql+pymysql://root:123456@localhost:3306/exam_point"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    ALGORITHM: str = "HS256"

    # Celery（上线后改为 True）
    USE_CELERY: bool = False

    # SMS
    SMS_MOCK: bool = True  # 开发阶段使用固定验证码

    # 微信小程序
    WX_APPID: str = "wx56063c50605f31d7"
    WX_SECRET: str = "8f9b16090da06ebf77841ea364f84ac4"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
