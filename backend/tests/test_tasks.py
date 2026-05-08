import pytest
from unittest.mock import patch, MagicMock
from app.worker.tasks import scrape_products_task

@patch('app.worker.tasks.TikTokIngestionEngine.extract_trending_data')
@patch('app.worker.tasks.SessionLocal')
@patch('app.worker.tasks.generate_and_queue_content_task.delay')
def test_scrape_products_task(mock_delay, mock_session, mock_extract):
    mock_db = MagicMock()
    mock_session.return_value = mock_db
    mock_db.query().filter().first.return_value = None

    mock_extracted_data = [{
        "video_id": "123",
        "caption": "Test",
        "trend_score": 90.0
    }]

    import asyncio
    future = asyncio.Future()

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def mock_extract_fn():
            return mock_extracted_data, "mock"

        mock_extract.side_effect = mock_extract_fn

    class MockSelf:
        retry = Exception

    res = scrape_products_task.apply().result

    assert res["status"] == "completed"
