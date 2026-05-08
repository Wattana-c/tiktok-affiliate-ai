from fastapi import APIRouter

from app.api.v1.endpoints import products, scraper, ai, scheduler, posting, accounts, queue, analytics

api_router = APIRouter()
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(scraper.router, prefix="/scraper", tags=["scraper"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(scheduler.router, prefix="/scheduler", tags=["scheduler"])
api_router.include_router(posting.router, prefix="/posting", tags=["posting"])
api_router.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
api_router.include_router(queue.router, prefix="/queue", tags=["queue"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
