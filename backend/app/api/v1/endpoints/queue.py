from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.post_queue import PostQueue as DBPostQueue
from app.models.generated_content import GeneratedContent
from app.schemas.queue import QueueItem, QueueMetricsUpdate

router = APIRouter()

@router.get("/", response_model=List[QueueItem])
def read_queue(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    queue_items = db.query(DBPostQueue).offset(skip).limit(limit).all()
    return queue_items

@router.put("/{queue_id}/approve")
def approve_queue_item(queue_id: int, db: Session = Depends(get_db)):
    db_item = db.query(DBPostQueue).filter(DBPostQueue.id == queue_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Queue item not found")

    if db_item.status != "review":
        raise HTTPException(status_code=400, detail="Item is not in review status")

    db_item.status = "pending"
    db.commit()
    db.refresh(db_item)
    return {"message": "Queue item approved for posting", "status": db_item.status}

@router.put("/{queue_id}/retry")
def retry_queue_item(queue_id: int, db: Session = Depends(get_db)):
    db_item = db.query(DBPostQueue).filter(DBPostQueue.id == queue_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Queue item not found")

    if db_item.status != "failed":
        raise HTTPException(status_code=400, detail="Only failed items can be retried")

    db_item.status = "pending"
    db_item.retry_count = 0
    db_item.error_message = None
    db.commit()
    db.refresh(db_item)
    return {"message": "Queue item marked for retry", "status": db_item.status}

@router.put("/{queue_id}/performance", response_model=QueueItem)
def update_queue_performance(queue_id: int, metrics: QueueMetricsUpdate, db: Session = Depends(get_db)):
    db_item = db.query(DBPostQueue).filter(DBPostQueue.id == queue_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Queue item not found")

    if db_item.status != "posted":
        raise HTTPException(status_code=400, detail="Can only update performance for posted items")

    for key, value in metrics.model_dump(exclude_unset=True).items():
        setattr(db_item, key, value)

    # Calculate a simple performance score to feedback to AI.
    # Score = (clicks * 5) + (conversions * 20) + (likes) + (shares * 3) + (comments * 2)
    score = (db_item.clicks * 5) + (db_item.conversions * 20) + db_item.likes + (db_item.shares * 3) + (db_item.comments * 2)

    db_content = db.query(GeneratedContent).filter(GeneratedContent.id == db_item.content_id).first()
    if db_content:
        db_content.performance_score = score

        # Track Strategy Metric
        from app.models.content_strategy_metrics import ContentStrategyMetrics
        metric = db.query(ContentStrategyMetrics).filter(
            ContentStrategyMetrics.metric_type == "content_mode",
            ContentStrategyMetrics.metric_value == db_content.content_mode
        ).first()

        if not metric:
            metric = ContentStrategyMetrics(metric_type="content_mode", metric_value=db_content.content_mode, total_uses=1, average_score=score)
            db.add(metric)
        else:
            metric.average_score = ((metric.average_score * metric.total_uses) + score) / (metric.total_uses + 1)
            metric.total_uses += 1

    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/{queue_id}")
def delete_queue_item(queue_id: int, db: Session = Depends(get_db)):
    db_item = db.query(DBPostQueue).filter(DBPostQueue.id == queue_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Queue item not found")
    db.delete(db_item)
    db.commit()
    return {"message": "Queue item deleted"}
