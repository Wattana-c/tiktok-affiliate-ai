import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.scraper.tiktok_scraper import TikTokIngestionEngine

@pytest.fixture
def engine():
    return TikTokIngestionEngine()

def test_trend_scoring_logic(engine):
    # Test high engagement scenario
    item_high = {
        "view_count": 100000,
        "like_count": 20000,
        "share_count": 5000
    }
    score_high = engine.calculate_trend_score(item_high)
    assert score_high > 80.0

    # Test low engagement scenario
    item_low = {
        "view_count": 10000,
        "like_count": 100,
        "share_count": 5
    }
    score_low = engine.calculate_trend_score(item_low)
    assert score_low < 50.0

    # Test edge case
    item_zero = {"view_count": 0}
    score_zero = engine.calculate_trend_score(item_zero)
    assert score_zero == 0.0

@pytest.mark.asyncio
async def test_extraction_fallback_mechanics(engine):
    # Mocking both API and Scraper to fail, forcing fallback to 'mock'
    with patch.object(engine, 'fetch_from_api', return_value=([], "api")) as mock_api:
        with patch.object(engine, 'fetch_from_scraping', return_value=([], "scrape")) as mock_scrape:
            data, source = await engine.extract_trending_data()

            assert mock_api.called
            assert mock_scrape.called
            assert source == "mock"
            assert len(data) > 0
            assert "trend_score" in data[0]

@pytest.mark.asyncio
async def test_extraction_api_success(engine):
    # Mock API to succeed
    mock_data = [{"video_id": "api_vid_1", "view_count": 500}]
    with patch.object(engine, 'fetch_from_api', return_value=(mock_data, "api")) as mock_api:
        data, source = await engine.extract_trending_data()

        assert mock_api.called
        assert source == "api"
        assert len(data) == 1
        assert data[0]["video_id"] == "api_vid_1"
