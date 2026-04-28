from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.product import Product as DBProduct
from app.schemas.product import Product, ProductCreate
from app.services.scraper.tiktok_scraper import scrape_tiktok_products_mock

router = APIRouter()

@router.post("/scrape-mock-products", response_model=List[Product])
async def scrape_mock_products(db: Session = Depends(get_db)):
    """
    Triggers the mock TikTok product scraper and saves the products to the database.
    """
    mock_products_data = await scrape_tiktok_products_mock()
    created_products = []
    for product_data in mock_products_data:
        # Check if product already exists to avoid duplicates
        existing_product = db.query(DBProduct).filter(DBProduct.tiktok_product_id == product_data.tiktok_product_id).first()
        if not existing_product:
            db_product = DBProduct(**product_data.model_dump())
            db.add(db_product)
            db.commit()
            db.refresh(db_product)
            created_products.append(db_product)
        else:
            # Optionally update existing product or just skip
            created_products.append(existing_product)
    return created_products
