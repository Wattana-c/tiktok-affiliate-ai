from sqlalchemy import Column, Integer, String, Float, DateTime, func, Text
from app.db.database import Base

class ViralPattern(Base):
    __tablename__ = "viral_patterns"

    id = Column(Integer, primary_key=True, index=True)
    pattern_type = Column(String, index=True) # "hook", "pain_point", "storytelling", "cta"
    content = Column(Text, nullable=False)
    language = Column(String, index=True)
    effectiveness_score = Column(Float, default=0.0) # Calculated based on how well this pattern performs
    times_used = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
