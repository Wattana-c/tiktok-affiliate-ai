from sqlalchemy import Column, Integer, String, Float, DateTime, func
from app.db.database import Base

class ContentStrategyMetrics(Base):
    __tablename__ = "content_strategy_metrics"

    id = Column(Integer, primary_key=True, index=True)
    metric_type = Column(String, index=True) # 'hook', 'content_mode', 'hashtag'
    metric_value = Column(String, index=True) # e.g. "soft_sell", "#Review", "Problem-Solution Hook"
    total_uses = Column(Integer, default=0)
    average_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
