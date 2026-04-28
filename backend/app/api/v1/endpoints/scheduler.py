from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import Dict

from app.services.scheduler.mock_scheduler import schedule_content_posting_mock

router = APIRouter()

@router.post("/schedule-posting/{product_id}", response_model=Dict[str, str])
async def schedule_posting(product_id: int, schedule_time: datetime):
    """
    Schedules a mock content posting for a given product ID at a specified time.
    """
    if schedule_time < datetime.now():
        raise HTTPException(status_code=400, detail="Schedule time must be in the future")
    
    result = await schedule_content_posting_mock(product_id, schedule_time)
    return result
