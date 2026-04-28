from app.worker.celery_app import celery_app
from app.services.scraper.tiktok_scraper import scrape_tiktok_products_mock
from app.services.ai.content_generator import generate_tiktok_content_mock
from app.services.posting.tiktok_poster import post_content_to_tiktok_mock
from app.db.database import SessionLocal
from app.models.product import Product as DBProduct
from app.schemas.product import Product

@celery_app.task(acks_late=True)
def scrape_products_task():
    db = SessionLocal()
    try:
        mock_products_data = scrape_tiktok_products_mock()
        for product_data in mock_products_data:
            existing_product = db.query(DBProduct).filter(DBProduct.tiktok_product_id == product_data.tiktok_product_id).first()
            if not existing_product:
                db_product = DBProduct(**product_data.model_dump())
                db.add(db_product)
                db.commit()
                db.refresh(db_product)
                print(f"Scraped and saved product: {db_product.name}")
            else:
                print(f"Product already exists, skipping: {existing_product.name}")
    finally:
        db.close()
    return {"status": "completed", "message": "Product scraping task finished."}

@celery_app.task(acks_late=True)
def generate_and_post_content_task(product_id: int):
    db = SessionLocal()
    try:
        db_product = db.query(DBProduct).filter(DBProduct.id == product_id).first()
        if db_product is None:
            print(f"Product with ID {product_id} not found.")
            return {"status": "failed", "message": f"Product with ID {product_id} not found."}
        
        product_schema = Product.model_validate(db_product)
        generated_content = generate_tiktok_content_mock(product_schema)
        post_result = post_content_to_tiktok_mock(product_id, generated_content)
        print(f"Generated and posted content for product ID {product_id}: {post_result}")
        return {"status": "completed", "message": "Content generation and posting task finished.", "result": post_result}
    finally:
        db.close()
