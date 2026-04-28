from typing import Dict

async def post_content_to_tiktok_mock(product_id: int, content: Dict[str, str]) -> Dict[str, str]:
    """
    Mocks the posting of content to TikTok.
    In a real scenario, this would interact with the TikTok API.
    """
    return {
        "message": f"Mock content posted to TikTok for product ID {product_id}",
        "product_id": str(product_id),
        "posted_content": content
    }
