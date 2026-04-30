from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict

from app.db.database import get_db
from app.models.product import Product as DBProduct
from app.schemas.product import Product
from app.services.ai.content_generator import generate_content
from app.services.posting.tiktok_poster import post_content_to_tiktok_mock

router = APIRouter()

@router.post("/post-content/{product_id}", response_model=Dict[str, str])
async def post_content(product_id: int, language: str = "Thai", db: Session = Depends(get_db)):
    """
    Generates content for a product and then mocks posting it to TikTok.
    """
    db_product = db.query(DBProduct).filter(DBProduct.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product_schema = Product.model_validate(db_product)
    generated_content = await generate_content(product_schema, language=language)
    post_result = await post_content_to_tiktok_mock(product_id, generated_content)
    return post_result
