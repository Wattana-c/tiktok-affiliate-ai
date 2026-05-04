from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from app.models.content_strategy_metrics import ContentStrategyMetrics
from app.models.product import Product as DBProduct
from app.models.post_queue import PostQueue
from pydantic import BaseModel

router = APIRouter()

class MetricResponse(BaseModel):
    metric_type: str
    metric_value: str
    total_uses: int
    average_score: float

@router.get("/top-styles", response_model=List[MetricResponse])
def get_top_styles(db: Session = Depends(get_db)):
    return db.query(ContentStrategyMetrics).order_by(ContentStrategyMetrics.average_score.desc()).limit(5).all()

@router.get("/dashboard-stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_conversions = db.query(func.sum(PostQueue.conversions)).scalar() or 0
    total_clicks = db.query(func.sum(PostQueue.clicks)).scalar() or 0
    total_revenue = db.query(func.sum(PostQueue.revenue)).scalar() or 0.0
    total_profit = db.query(func.sum(PostQueue.profit_score)).scalar() or 0.0

    top_product = db.query(DBProduct).order_by(DBProduct.trend_score.desc()).first()

    return {
        "total_conversions": total_conversions,
        "total_clicks": total_clicks,
        "total_revenue": total_revenue,
        "total_profit": total_profit,
        "conversion_rate": round((total_conversions / total_clicks * 100) if total_clicks > 0 else 0, 2),
        "top_product_name": top_product.name if top_product else "N/A",
        "top_product_score": top_product.trend_score if top_product else 0
    }

@router.get("/top-niches")
def get_top_niches(db: Session = Depends(get_db)):
    from app.models.niche_performance import NichePerformance
    niches = db.query(NichePerformance).order_by(NichePerformance.total_profit.desc()).limit(5).all()
    return niches
