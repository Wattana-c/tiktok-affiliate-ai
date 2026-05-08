from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import random

from app.db.database import get_db
from app.models.product import Product as DBProduct
from app.schemas.product import Product, ProductCreate
from app.services.scraper.tiktok_scraper import TikTokIngestionEngine
from app.worker.tasks import generate_and_queue_content_task

router = APIRouter()

@router.post("/scrape-mock-products", response_model=List[Product])
async def scrape_mock_products(db: Session = Depends(get_db)):
    """
    Triggers the TikTok product scraper and saves the products to the database.
    It will also assign a calculated trend score and trigger content generation automatically.
    """
    engine = TikTokIngestionEngine()
    mock_products_data, _ = await engine.extract_trending_data()

    created_products = []
    for item in mock_products_data:
        # Check if product already exists to avoid duplicates
        video_id = item.get("video_id")
        existing_product = db.query(DBProduct).filter(DBProduct.tiktok_product_id == video_id).first()
        if not existing_product:
            product_data = {
                "tiktok_product_id": video_id,
                "name": item.get("product_keywords", "Trending Product"),
                "description": item.get("caption", ""),
                "price": 0.0,
                "trend_score": item.get("trend_score", 0.0)
            }
            db_product = DBProduct(**product_data)
            db.add(db_product)
            db.commit()
            db.refresh(db_product)
            created_products.append(db_product)

            # Automatically trigger generation for this product
            generate_and_queue_content_task.delay(db_product.id, "Thai")
            generate_and_queue_content_task.delay(db_product.id, "English")
        else:
            # Optionally update existing product or just skip
            created_products.append(existing_product)
    return created_products
