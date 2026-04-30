from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.post_queue import PostQueue as DBPostQueue
from app.schemas.queue import QueueItem

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

@router.delete("/{queue_id}")
def delete_queue_item(queue_id: int, db: Session = Depends(get_db)):
    db_item = db.query(DBPostQueue).filter(DBPostQueue.id == queue_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Queue item not found")
    db.delete(db_item)
    db.commit()
    return {"message": "Queue item deleted"}
