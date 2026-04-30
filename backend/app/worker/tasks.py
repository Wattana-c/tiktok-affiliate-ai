import asyncio
import logging
import json
from datetime import datetime, timedelta
from celery.exceptions import MaxRetriesExceededError
from app.worker.celery_app import celery_app
from app.services.scraper.tiktok_scraper import scrape_tiktok_products_mock
from app.services.ai.content_generator import generate_variants
from app.services.posting.tiktok_poster import post_content_to_tiktok_mock
from app.db.database import SessionLocal
from app.models.product import Product as DBProduct
from app.models.generated_content import GeneratedContent
from app.models.post_queue import PostQueue
from app.models.account import Account
from app.schemas.product import Product

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, acks_late=True, max_retries=3, default_retry_delay=60)
def scrape_products_task(self):
    db = SessionLocal()
    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        mock_products_data = loop.run_until_complete(scrape_tiktok_products_mock())

        for product_data in mock_products_data:
            existing_product = db.query(DBProduct).filter(DBProduct.tiktok_product_id == product_data.tiktok_product_id).first()
            if not existing_product:
                # Add mock trend score out of 100
                import random
                product_data.trend_score = round(random.uniform(30.0, 100.0), 1)

                db_product = DBProduct(**product_data.model_dump())
                db.add(db_product)
                db.commit()
                db.refresh(db_product)
                logger.info(json.dumps({
                    "event": "product_scraped",
                    "product_id": db_product.id,
                    "trend_score": db_product.trend_score
                }))

                # Smart Decision Logic based on trend_score
                if db_product.trend_score < 50:
                    logger.info(json.dumps({"event": "skip_product", "product_id": db_product.id, "reason": "Low trend score"}))
                    continue

                # Automatically trigger content generation after scraping
                generate_and_queue_content_task.delay(db_product.id, "Thai")
            else:
                logger.info(f"Product already exists, skipping: {existing_product.name}")
    except Exception as e:
        logger.error(json.dumps({"event": "scrape_error", "error": str(e)}))
        try:
            raise self.retry(exc=e)
        except MaxRetriesExceededError:
            logger.error(json.dumps({"event": "scrape_failed_max_retries"}))
    finally:
        db.close()
    return {"status": "completed", "message": "Product scraping task finished."}

@celery_app.task(bind=True, acks_late=True, max_retries=3, default_retry_delay=60)
def generate_and_queue_content_task(self, product_id: int, language: str = "Thai"):
    db = SessionLocal()
    try:
        db_product = db.query(DBProduct).filter(DBProduct.id == product_id).first()
        if db_product is None:
            logger.warning(f"Product with ID {product_id} not found.")
            return {"status": "failed", "message": f"Product with ID {product_id} not found."}
        
        # Duplicate content detection
        existing_content = db.query(GeneratedContent).filter(
            GeneratedContent.product_id == product_id,
            GeneratedContent.language == language
        ).first()

        if existing_content:
            logger.info(json.dumps({"event": "content_skipped", "reason": "Already exists", "product_id": product_id}))
            return {"status": "skipped", "message": "Content already exists"}

        product_schema = Product.model_validate(db_product)

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        generated_variants = loop.run_until_complete(generate_variants(product_schema, language))

        saved_contents = []
        for variant in generated_variants:
            new_content = GeneratedContent(
                product_id=product_id,
                language=language,
                content_mode=variant.get("content_mode", "soft_sell"),
                variant_name=variant.get("variant_name", "Variant A"),
                hook=variant.get("hook", ""),
                caption=variant.get("caption", ""),
                video_script=variant.get("video_script", ""),
                cta=variant.get("cta", ""),
                hashtags=variant.get("hashtags", "")
            )
            db.add(new_content)
            saved_contents.append(new_content)

        db.commit()
        for content in saved_contents:
            db.refresh(content)

        logger.info(json.dumps({"event": "content_generated", "product_id": product_id, "variants": len(saved_contents)}))

        # Pick the first variant to queue
        if saved_contents:
            target_content = saved_contents[0]

            # Automatically queue for posting (Find an active account)
            account = db.query(Account).filter(Account.is_active == True).first()
            if account:
                # Smart decision for Queue status
                queue_status = "pending" if db_product.trend_score >= 80 else "review"

                schedule_time = datetime.now() + timedelta(minutes=5)
                queue_item = PostQueue(
                    product_id=product_id,
                    account_id=account.id,
                    content_id=target_content.id,
                    status=queue_status,
                    scheduled_time=schedule_time
                )
                db.add(queue_item)
                db.commit()
                logger.info(json.dumps({
                    "event": "content_queued",
                    "queue_id": queue_item.id,
                    "status": queue_status,
                    "scheduled_time": str(schedule_time)
                }))
            else:
                logger.warning(json.dumps({"event": "queue_failed", "reason": "No active accounts found"}))

        return {"status": "completed", "message": "Content generation and queuing task finished."}
    except Exception as e:
        logger.error(json.dumps({"event": "generate_error", "error": str(e)}))
        try:
            raise self.retry(exc=e)
        except MaxRetriesExceededError:
            logger.error(json.dumps({"event": "generate_failed_max_retries"}))
            return {"status": "failed", "message": str(e)}
    finally:
        db.close()

@celery_app.task(bind=True, acks_late=True, max_retries=5, default_retry_delay=300) # Exponential backoff recommended in prod
def post_queued_content_task(self):
    db = SessionLocal()
    try:
        now = datetime.now()
        pending_posts = db.query(PostQueue).filter(
            PostQueue.status == "pending",
            PostQueue.scheduled_time <= now
        ).all()

        for post in pending_posts:
            account = db.query(Account).filter(Account.id == post.account_id).first()
            if not account or not account.is_active:
                post.status = "failed"
                post.error_message = "Account disabled or not found"
                db.commit()
                continue

            content = db.query(GeneratedContent).filter(GeneratedContent.id == post.content_id).first()
            if not content:
                post.status = "failed"
                post.error_message = "Content not found"
                db.commit()
                continue

            try:
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                post_result = loop.run_until_complete(post_content_to_tiktok_mock(post.product_id, {"caption": content.caption}))

                post.status = "posted"
                post.posted_time = now
                db.commit()
                logger.info(json.dumps({"event": "post_success", "queue_id": post.id, "result": post_result}))
            except Exception as post_err:
                post.retry_count += 1
                if post.retry_count >= 5:
                    post.status = "failed"
                    post.error_message = f"Max retries exceeded. Error: {str(post_err)}"

                    # Auto disable account logic
                    if account:
                        account.failed_attempts += 1
                        if account.failed_attempts >= 5:
                            account.is_active = False
                            logger.error(json.dumps({"event": "account_auto_disabled", "account_id": account.id}))
                else:
                    post.error_message = str(post_err)
                db.commit()
                raise post_err # Re-raise to trigger Celery retry

        return {"status": "completed", "message": f"Processed {len(pending_posts)} pending posts."}
    except Exception as e:
        logger.error(json.dumps({"event": "post_task_error", "error": str(e)}))
        try:
            # Simple exponential backoff for Celery retry
            raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
        except MaxRetriesExceededError:
            logger.error(json.dumps({"event": "post_task_failed_max_retries"}))
            return {"status": "failed", "message": str(e)}
    finally:
        db.close()
