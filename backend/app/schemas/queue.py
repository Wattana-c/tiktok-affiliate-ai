from pydantic import BaseModel, Field, model_validator
from typing import Optional
from datetime import datetime

class QueueBase(BaseModel):
    product_id: int
    account_id: int
    content_id: int
    status: Optional[str] = "pending"
    scheduled_time: Optional[datetime] = None

class QueueCreate(QueueBase):
    pass

class QueueMetricsUpdate(BaseModel):
    views: Optional[int] = Field(None, ge=0)
    likes: Optional[int] = Field(None, ge=0)
    comments: Optional[int] = Field(None, ge=0)
    shares: Optional[int] = Field(None, ge=0)
    clicks: Optional[int] = Field(None, ge=0)
    conversions: Optional[int] = Field(None, ge=0)
    revenue: Optional[float] = Field(None, ge=0.0, description="Revenue must be non-negative")

    @model_validator(mode='after')
    def validate_conversion_rate(self) -> 'QueueMetricsUpdate':
        if self.views is not None and self.conversions is not None:
            if self.conversions > self.views:
                raise ValueError(f"Conversions ({self.conversions}) cannot exceed views ({self.views}). Conversion rate must be <= 1.0.")
        return self

class QueueItem(QueueBase):
    id: int
    retry_count: Optional[int] = 0
    posted_time: Optional[datetime] = None
    error_message: Optional[str] = None
    views: Optional[int] = 0
    likes: Optional[int] = 0
    comments: Optional[int] = 0
    shares: Optional[int] = 0
    clicks: Optional[int] = 0
    conversions: Optional[int] = 0
    revenue: Optional[float] = 0.0
    profit_score: Optional[float] = 0.0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
