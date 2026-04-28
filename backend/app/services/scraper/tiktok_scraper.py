from typing import List
from app.schemas.product import ProductCreate

async def scrape_tiktok_products_mock() -> List[ProductCreate]:
    """
    Mocks the scraping of TikTok affiliate products.
    Returns a list of ProductCreate schemas.
    """
    mock_products = [
        ProductCreate(
            tiktok_product_id="tiktok_prod_001",
            name="เครื่องดูดฝุ่นไร้สายพลังสูง",
            description="เครื่องดูดฝุ่นไร้สายที่มาพร้อมพลังดูดมหาศาล ทำความสะอาดบ้านได้หมดจดทุกซอกทุกมุม",
            price=2599.00,
            currency="THB",
            product_url="https://www.tiktok.com/product/tiktok_prod_001",
            image_url="https://example.com/images/prod_001.jpg",
            category="เครื่องใช้ไฟฟ้าในบ้าน"
        ),
        ProductCreate(
            tiktok_product_id="tiktok_prod_002",
            name="ชุดออกกำลังกายโยคะพรีเมียม",
            description="ชุดออกกำลังกายสำหรับโยคะและพิลาทิส เนื้อผ้านุ่มสบาย ระบายอากาศได้ดีเยี่ยม",
            price=899.00,
            currency="THB",
            product_url="https://www.tiktok.com/product/tiktok_prod_002",
            image_url="https://example.com/images/prod_002.jpg",
            category="แฟชั่นและกีฬา"
        ),
        ProductCreate(
            tiktok_product_id="tiktok_prod_003",
            name="หูฟังบลูทูธตัดเสียงรบกวน",
            description="หูฟังไร้สายคุณภาพเสียงคมชัด พร้อมระบบตัดเสียงรบกวนอัจฉริยะ เหมาะสำหรับคนรักเสียงเพลง",
            price=1999.00,
            currency="THB",
            product_url="https://www.tiktok.com/product/tiktok_prod_003",
            image_url="https://example.com/images/prod_003.jpg",
            category="อิเล็กทรอนิกส์"
        ),
    ]
    return mock_products
