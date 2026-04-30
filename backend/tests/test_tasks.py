import pytest
from unittest.mock import patch, MagicMock
from app.worker.tasks import scrape_products_task

@patch('app.worker.tasks.scrape_tiktok_products_mock')
@patch('app.worker.tasks.SessionLocal')
@patch('app.worker.tasks.generate_and_queue_content_task.delay')
def test_scrape_products_task(mock_delay, mock_session, mock_scrape):
    mock_db = MagicMock()
    mock_session.return_value = mock_db
    mock_db.query().filter().first.return_value = None

    class MockProduct:
        def __init__(self):
            self.tiktok_product_id = "123"
            self.name = "Test"
            self.trend_score = 90.0
            self.description = "Test Desc"
            self.price = 100.0
            self.currency = "THB"
            self.product_url = "http://test"
            self.image_url = "http://test"
            self.category = "test"
        def model_dump(self):
            return {"tiktok_product_id": "123", "name": "Test"}

    import asyncio
    future = asyncio.Future()

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    future = loop.create_future()
    future.set_result([MockProduct()])
    mock_scrape.return_value = future

    class MockSelf:
        retry = Exception

    res = scrape_products_task.apply().result

    assert res["status"] == "completed"
