from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict

from typing import Dict, List
from app.db.database import get_db
from app.models.product import Product as DBProduct
from app.schemas.product import Product
from app.services.ai.content_generator import generate_content, generate_variants

router = APIRouter()

@router.post("/generate-content/{product_id}", response_model=Dict[str, str])
async def generate_content_for_product(product_id: int, language: str = "Thai", mode: str = "soft_sell", db: Session = Depends(get_db)):
    """
    Generates AI TikTok/Facebook content for a given product ID and language.
    """
    db_product = db.query(DBProduct).filter(DBProduct.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product_schema = Product.model_validate(db_product)
    content = await generate_content(product_schema, language=language, content_mode=mode)
    return content

@router.post("/generate-variants/{product_id}")
async def generate_variants_for_product(product_id: int, language: str = "Thai", db: Session = Depends(get_db)):
    """
    Generates multiple variants (A/B testing) for a given product ID.
    """
    db_product = db.query(DBProduct).filter(DBProduct.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    product_schema = Product.model_validate(db_product)
    variants = await generate_variants(product_schema, language=language)
    return variants
