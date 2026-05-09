from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, func
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
    is_shadowbanned = Column(Boolean, default=False)
    total_profit = Column(Float, default=0.0)
    account_cost = Column(Float, default=0.15)
    proxy_cost = Column(Float, default=0.25)
    trust_score = Column(Float, default=50.0) # Used to prioritize routing, max 100
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
