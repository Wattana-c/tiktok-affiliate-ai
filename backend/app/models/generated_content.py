from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from app.db.database import Base

class GeneratedContent(Base):
    __tablename__ = "generated_contents"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    language = Column(String) # e.g., "th", "en"
    content_mode = Column(String, default="soft_sell")
    variant_name = Column(String, default="Variant A")
    hook = Column(Text)
    caption = Column(Text)
    video_script = Column(Text)
    cta = Column(Text)
    hashtags = Column(Text)
    created_at = Column(DateTime, default=func.now())
