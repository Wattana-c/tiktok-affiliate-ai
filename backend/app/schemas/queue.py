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

class QueueItem(QueueBase):
    id: int
    retry_count: Optional[int] = 0
    posted_time: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
