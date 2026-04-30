from sqlalchemy import Column, Integer, String, Text, DateTime, Float, func
from app.db.database import Base

class TikTokVideoTrend(Base):
    __tablename__ = "tiktok_video_trends"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String, unique=True, index=True)
    caption = Column(Text, nullable=True)
    hashtags = Column(Text, nullable=True)
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    product_keywords = Column(String, nullable=True)
    source = Column(String, default="mock") # "api", "scrape", "mock"
    trend_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
