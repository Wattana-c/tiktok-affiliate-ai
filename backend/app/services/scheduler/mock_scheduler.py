from datetime import datetime
from typing import Dict

async def schedule_content_posting_mock(product_id: int, schedule_time: datetime) -> Dict[str, str]:
    """
    Mocks the scheduling of content posting.
    In a real scenario, this would interact with a task queue like Celery Beat.
    """
    return {
        "message": f"Mock posting for product ID {product_id} scheduled for {schedule_time.isoformat()}",
        "product_id": str(product_id),
        "scheduled_time": schedule_time.isoformat()
    }
