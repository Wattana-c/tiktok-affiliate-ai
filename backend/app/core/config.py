import os
from pydantic_settings import BaseSettings
import os
load_dotenv = lambda: None
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class Settings(BaseSettings):
    PROJECT_NAME: str = "TikTok Affiliate AI Auto Content Machine"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./tiktok_affiliate.db")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

    INFRA_COST_PER_POST: float = 0.10

    # Global Risk Control (Kill Switch)
    DAILY_LOSS_LIMIT: float = float(os.getenv("DAILY_LOSS_LIMIT", "-20.0"))

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
