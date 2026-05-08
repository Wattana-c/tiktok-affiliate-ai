from sqlalchemy import Column, Integer, String, Text, Float, DateTime, func
from sqlalchemy.orm import relationship
from app.db.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    tiktok_product_id = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float)
    currency = Column(String, default="THB")
    estimated_commission = Column(Float, default=0.0)
    product_url = Column(String, unique=True)
    image_url = Column(String, nullable=True)
    category = Column(String, nullable=True)
    trend_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    generated_contents = relationship("GeneratedContent", back_populates="product", cascade="all, delete-orphan")
