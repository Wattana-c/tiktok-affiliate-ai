from sqlalchemy import Column, Integer, String, Float, DateTime, func
from app.db.database import Base

class NichePerformance(Base):
    __tablename__ = "niche_performance"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, unique=True, index=True)
    total_posts = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    total_profit = Column(Float, default=0.0)
    avg_conversion_rate = Column(Float, default=0.0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
