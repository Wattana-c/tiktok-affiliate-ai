from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Float, func, CheckConstraint
from app.db.database import Base

class PostQueue(Base):
    __tablename__ = "post_queue"
    __table_args__ = (
        CheckConstraint('revenue >= 0', name='check_revenue_positive'),
    )

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    account_id = Column(Integer, ForeignKey("accounts.id"))
    content_id = Column(Integer, ForeignKey("generated_contents.id"))
    status = Column(String, default="pending") # "pending", "review", "posted", "failed"
    retry_count = Column(Integer, default=0)
    scheduled_time = Column(DateTime, nullable=True)
    posted_time = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    revenue = Column(Float, default=0.0)
    dynamic_cost = Column(Float, default=0.0)
    profit_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
