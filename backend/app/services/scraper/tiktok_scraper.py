import random
import logging
import asyncio
import httpx
from typing import List, Dict, Any, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/120.0.6099.119 Mobile/15E148 Safari/604.1"
]

class TikTokIngestionEngine:
    def __init__(self):
        self.creative_center_url = "https://ads.tiktok.com/business/creativecenter/inspiration/popular/pc/en" # Replace with valid CC endpoint
        self.api_url = "https://mock-tiktok-api.example.com/v1/trending" # Replace with real API if available
        self.scrape_url = "https://www.tiktok.com/explore"

    def _get_random_headers(self) -> Dict[str, str]:
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

    async def fetch_from_creative_center(self) -> Tuple[List[Dict[str, Any]], str]:
        """Primary method: Attempt to fetch from TikTok Creative Center for official trending data."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(self.creative_center_url, headers=self._get_random_headers())
                if response.status_code == 200:
                    # In a real scenario, extract data from creative center API/HTML
                    # We simulate successful extraction here
                    pass
                else:
                    logger.warning(f"Creative Center Blocked/Rate Limited (Status {response.status_code}).")
        except httpx.RequestError as e:
            logger.warning(f"Creative Center Request Exception: {e}")
        return [], "creative_center"

    async def fetch_from_api(self) -> Tuple[List[Dict[str, Any]], str]:
        """Secondary method: Attempt to fetch from official/third-party API."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(self.api_url, headers=self._get_random_headers())
                if response.status_code == 200:
                    data = response.json()
                    return data.get("videos", []), "api"
                elif response.status_code in [401, 403, 429]:
                    logger.warning(f"API Blocked/Rate Limited (Status {response.status_code}).")
                else:
                    logger.warning(f"API Request failed with status {response.status_code}.")
        except httpx.RequestError as e:
            logger.warning(f"API Request Exception: {e}")
        return [], "api"

    async def fetch_from_scraping(self) -> Tuple[List[Dict[str, Any]], str]:
        """Tertiary method: Fallback to web scraping."""
        try:
            # Throttling
            await asyncio.sleep(random.uniform(1.0, 3.0))

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.scrape_url, headers=self._get_random_headers())

                # Detect block response (e.g., Captcha page or 403)
                if response.status_code == 403 or "captcha" in response.text.lower():
                    logger.error("Scraping blocked by TikTok Anti-Bot.")
                    return [], "scrape"

                if response.status_code == 200:
                    # In a real scenario, we would parse response.text using BeautifulSoup/Playwright here.
                    # For demonstration, we simulate finding 1 item if successful.
                    return [{"video_id": f"scraped_{random.randint(1000,9999)}", "caption": "Scraped trending product!", "view_count": 50000}], "scrape"
        except httpx.RequestError as e:
            logger.error(f"Scraping Request Exception: {e}")
        return [], "scrape"

    async def fetch_from_mock(self) -> Tuple[List[Dict[str, Any]], str]:
        """Fallback method: Return highly realistic mock data."""
        logger.info("Using mock fallback data.")
        mock_data = [
            {
                "video_id": f"mock_vid_{random.randint(10000, 99999)}",
                "caption": "รีวิวเครื่องดูดฝุ่นไร้สาย ตัวนี้แรงดูดสะใจมาก! #ของดีบอกต่อ #รีวิวช้อปปี้",
                "hashtags": "#ของดีบอกต่อ #รีวิวช้อปปี้ #เครื่องดูดฝุ่นไร้สาย",
                "view_count": random.randint(10000, 1000000),
                "like_count": random.randint(1000, 100000),
                "share_count": random.randint(100, 5000),
                "product_keywords": "เครื่องดูดฝุ่นไร้สาย"
            },
            {
                "video_id": f"mock_vid_{random.randint(10000, 99999)}",
                "caption": "This noise-cancelling headphone is a game changer! 🎧 #tech #review",
                "hashtags": "#tech #review #headphones",
                "view_count": random.randint(50000, 2000000),
                "like_count": random.randint(5000, 200000),
                "share_count": random.randint(500, 10000),
                "product_keywords": "noise-cancelling headphone"
            }
        ]
        return mock_data, "mock"

    def calculate_trend_score(self, item: Dict[str, Any]) -> float:
        """
        Calculates a trend score (0-100) based on engagement metrics.
        Formula considers engagement rate (likes/views), share velocity proxy, and raw view counts.
        """
        views = item.get("view_count", 0)
        likes = item.get("like_count", 0)
        shares = item.get("share_count", 0)

        if views == 0:
            return 0.0

        # Engagement rate (likes per view)
        engagement_rate = (likes / views) * 100

        # Share ratio (highly indicative of virality)
        share_ratio = (shares / views) * 1000

        # Base score from engagement
        base_score = min(engagement_rate * 5 + share_ratio * 10, 80)

        # View count bonus (up to 20 points for highly viewed videos)
        view_bonus = min(views / 50000, 20)

        # Final Score
        score = min(base_score + view_bonus, 100.0)
        return round(score, 1)

    async def extract_trending_data(self) -> Tuple[List[Dict[str, Any]], str]:
        """Orchestrates the fallback mechanism and applies scoring."""
        data = []
        source = "mock"

        # 1. Try Creative Center
        cc_data, cc_source = await self.fetch_from_creative_center()
        if cc_data:
            data, source = cc_data, cc_source
        else:
            logger.warning("Creative Center failed. Falling back to API.")

            # 2. Try API
            api_data, api_source = await self.fetch_from_api()
            if api_data:
                data, source = api_data, api_source
            else:
                logger.warning("API failed. Falling back to Scraper.")

                # 3. Try Scraping
                scrape_data, scrape_source = await self.fetch_from_scraping()
                if scrape_data:
                    data, source = scrape_data, scrape_source
                else:
                    logger.error("Scraper failed. Falling back to Mock data.")

                    # 4. Fallback to Mock
                    data, source = await self.fetch_from_mock()

        # Enhance data with calculated scores
        for item in data:
            item["trend_score"] = self.calculate_trend_score(item)

        return data, source
