from pydantic import BaseModel
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
    views: Optional[int] = None
    likes: Optional[int] = None
    comments: Optional[int] = None
    shares: Optional[int] = None
    clicks: Optional[int] = None
    conversions: Optional[int] = None

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
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
