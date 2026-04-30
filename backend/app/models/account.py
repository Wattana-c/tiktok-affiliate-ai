from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from app.db.database import Base

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String, index=True) # e.g., "tiktok", "facebook"
    account_name = Column(String)
    access_token = Column(String)
    is_active = Column(Boolean, default=True)
    rate_limit = Column(Integer, default=5) # Posts per day
    failed_attempts = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
