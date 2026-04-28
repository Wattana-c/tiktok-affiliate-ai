from typing import Dict
from app.schemas.product import Product

async def generate_tiktok_content_mock(product: Product) -> Dict[str, str]:
    """
    Mocks the AI content generation for a given product.
    Returns a dictionary with mock caption, hashtags, and script idea.
    """
    caption = f"🔥 ต้องมี! {product.name} แค่ {product.price} {product.currency} เท่านั้น! คลิกเลยที่ลิงก์ใน Bio! #{product.category.replace(" ", "")} #ของดีบอกต่อ #TikTokShop"
    hashtags = f"#{product.name.replace(" ", "")} #รีวิวสินค้า #โปรโมชั่น"
    script_idea = f"รีวิวการใช้งาน {product.name} แบบละเอียด โชว์ฟีเจอร์เด่นและประโยชน์ที่ได้รับ พร้อมสาธิตการใช้งานจริง"

    return {
        "caption": caption,
        "hashtags": hashtags,
        "script_idea": script_idea
    }
