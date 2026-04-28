from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict

from app.db.database import get_db
from app.models.product import Product as DBProduct
from app.schemas.product import Product
from app.services.ai.content_generator import generate_tiktok_content_mock

router = APIRouter()

@router.post("/generate-content/{product_id}", response_model=Dict[str, str])
async def generate_content_for_product(product_id: int, db: Session = Depends(get_db)):
    """
    Generates mock TikTok content for a given product ID.
    """
    db_product = db.query(DBProduct).filter(DBProduct.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product_schema = Product.model_validate(db_product)
    content = await generate_tiktok_content_mock(product_schema)
    return content
