import asyncio
import logging
import json
from datetime import datetime, timedelta
from celery.exceptions import MaxRetriesExceededError
from app.worker.celery_app import celery_app
from app.services.scraper.tiktok_scraper import TikTokIngestionEngine
from app.services.ai.content_generator import generate_variants
from app.services.posting.tiktok_poster import post_content_to_tiktok_mock
from app.models.tiktok_video_trend import TikTokVideoTrend
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

        engine = TikTokIngestionEngine()
        trending_data, source = loop.run_until_complete(engine.extract_trending_data())

        logger.info(json.dumps({
            "event": "data_ingestion_complete",
            "source": source,
            "items_extracted": len(trending_data),
            "freshness": str(datetime.now())
        }))

        for item in trending_data:
            # 1. Save raw extracted data to TikTokVideoTrend
            existing_trend = db.query(TikTokVideoTrend).filter(TikTokVideoTrend.video_id == item["video_id"]).first()
            if not existing_trend:
                trend_entry = TikTokVideoTrend(
                    video_id=item["video_id"],
                    caption=item.get("caption"),
                    hashtags=item.get("hashtags"),
                    view_count=item.get("view_count", 0),
                    like_count=item.get("like_count", 0),
                    share_count=item.get("share_count", 0),
                    product_keywords=item.get("product_keywords"),
                    source=source,
                    trend_score=item.get("trend_score", 0.0)
                )
                db.add(trend_entry)
                db.commit()

            # 2. Map back to products and trigger generation if applicable
            # In a real scenario we use the product_keywords to map or create the product.
            # Here we simulate by creating a product entry to match the trend logic.
            product_data = {
                "tiktok_product_id": item["video_id"], # Mapping proxy
                "name": item.get("product_keywords", "Trending Product"),
                "description": item.get("caption", ""),
                "price": 0.0,
                "trend_score": item.get("trend_score", 0.0)
            }

            existing_product = db.query(DBProduct).filter(DBProduct.tiktok_product_id == product_data["tiktok_product_id"]).first()
            if not existing_product:
                # Assign synthetic estimated_commission based on trend_score * rand for mock testing
                import random
                product_data["estimated_commission"] = round(product_data.get("trend_score", 0) * random.uniform(0.5, 2.0), 2)

                db_product = DBProduct(**product_data)
                db.add(db_product)
                db.commit()
                db.refresh(db_product)
                logger.info(json.dumps({
                    "event": "product_scraped",
                    "product_id": db_product.id,
                    "trend_score": db_product.trend_score,
                    "estimated_commission": db_product.estimated_commission
                }))

                # Smart Decision Logic based on trend_score and margins
                if db_product.trend_score < 50 and db_product.estimated_commission < 20.0:
                    logger.info(json.dumps({"event": "skip_product", "product_id": db_product.id, "reason": "Low trend score and low margin"}))
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
                hashtags=variant.get("hashtags", ""),
                diversity_penalty=variant.get("diversity_penalty", 0)
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

            # Multi-Account Scaling Engine: Rotate accounts by picking the one least used today, factoring in trust_score
            from sqlalchemy import func
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

            accounts = db.query(Account, func.count(PostQueue.id).label('daily_posts')).outerjoin(
                PostQueue,
                (PostQueue.account_id == Account.id) & (PostQueue.posted_time >= today_start) & (PostQueue.status == "posted")
            ).filter(
                Account.is_active == True,
                Account.is_shadowbanned == False
            ).group_by(Account.id).order_by(Account.trust_score.desc(), 'daily_posts').all()

            account = accounts[0][0] if accounts else None

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

        # Budget Allocation Logic: Sort pending posts dynamically by profit_score to ensure highest margin items post first.
        pending_posts = db.query(PostQueue).join(DBProduct).filter(
            PostQueue.status == "pending",
            PostQueue.scheduled_time <= now
        ).order_by(DBProduct.estimated_commission.desc()).all()

        # Global Risk Control: Daily Loss Limit
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        from sqlalchemy import func
        from app.core.config import settings

        daily_profit = db.query(func.sum(PostQueue.profit_score)).filter(PostQueue.posted_time >= today_start).scalar() or 0.0

        if daily_profit <= settings.DAILY_LOSS_LIMIT:
            logger.critical(json.dumps({
                "event": "CRITICAL_RISK_CONTROL_STOP",
                "reason": f"System-wide kill switch engaged. Daily profit ({daily_profit}) breached loss limit ({settings.DAILY_LOSS_LIMIT}).",
                "daily_profit": daily_profit
            }))
            return {"status": "halted", "message": "Risk control triggered: Daily loss limit reached."}

        # Group posts by account to enforce rate limits
        account_posts = {}
        for p in pending_posts:
            if p.account_id not in account_posts:
                account_posts[p.account_id] = []
            account_posts[p.account_id].append(p)

        for account_id, posts in account_posts.items():
            account = db.query(Account).filter(Account.id == account_id).first()
            if not account or not account.is_active or account.is_shadowbanned:
                for post in posts:
                    post.status = "failed"
                    reason = "Account is explicitly disabled or shadowbanned." if account else "Account not found."
                    post.error_message = reason
                    logger.warning(json.dumps({
                        "event": "post_skipped",
                        "post_id": post.id,
                        "account_id": account_id,
                        "reason": reason
                    }))
                db.commit()
                continue

            # Smart Posting Strategy: Enforce daily limits to avoid spam behavior
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            posted_today = db.query(PostQueue).filter(
                PostQueue.account_id == account.id,
                PostQueue.status == "posted",
                PostQueue.posted_time >= today_start
            ).count()

            allowed_posts_remaining = max(0, (account.rate_limit or 5) - posted_today)

            for post in posts:
                if allowed_posts_remaining <= 0:
                    logger.info(json.dumps({"event": "post_delayed_ratelimit", "account": account.id, "post": post.id}))
                    # Push scheduled time back
                    post.scheduled_time = datetime.now() + timedelta(hours=4)
                    db.commit()
                    continue

                allowed_posts_remaining -= 1

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
