from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional

class ProductBase(BaseModel):
    tiktok_product_id: str
    name: str
    description: Optional[str] = None
    price: float
    currency: str = "THB"
    product_url: HttpUrl
    image_url: Optional[HttpUrl] = None
    category: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    pass

class ProductInDBBase(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Product(ProductInDBBase):
    pass
