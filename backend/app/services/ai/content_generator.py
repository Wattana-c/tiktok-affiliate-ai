import json
import os
import asyncio
from typing import Dict, List
from openai import AsyncOpenAI
from app.schemas.product import Product
from app.services.ai.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE, FEEDBACK_CONTEXT_TEMPLATE
from app.db.database import SessionLocal
from app.models.generated_content import GeneratedContent
from app.models.product import Product as DBProduct
import logging

logger = logging.getLogger(__name__)

openai_api_key = os.getenv("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=openai_api_key) if openai_api_key else None

def get_high_performing_examples(category: str, language: str, limit: int = 2) -> str:
    """Fetches high performing content from the DB to use as examples in the prompt."""
    db = SessionLocal()
    try:
        query = db.query(GeneratedContent).join(DBProduct).filter(
            GeneratedContent.language == language,
            GeneratedContent.performance_score > 50
        )
        if category:
            query = query.filter(DBProduct.category == category)

        top_contents = query.order_by(GeneratedContent.performance_score.desc()).limit(limit).all()

        if not top_contents:
            return ""

        examples_str = ""
        for idx, content in enumerate(top_contents):
            examples_str += f"\nExample {idx+1}:\n"
            examples_str += f"Hook: {content.hook}\n"
            examples_str += f"Caption: {content.caption}\n"
            examples_str += f"CTA: {content.cta}\n"

        return FEEDBACK_CONTEXT_TEMPLATE.format(examples=examples_str)
    except Exception as e:
        logger.error(f"Error fetching examples: {e}")
        return ""
    finally:
        db.close()

async def generate_content(product: Product, language: str = "Thai", content_mode: str = "soft_sell") -> Dict[str, str]:
    """
    Generates AI affiliate content using OpenAI for a specific mode.
    Falls back to smart mock if no API key is provided.
    """
    if not client:
        logger.warning(f"OPENAI_API_KEY not found. Falling back to smart mocks ({content_mode}).")
        return _generate_smart_mock(product, language, content_mode)

    feedback_context = get_high_performing_examples(product.category, language)

    user_prompt = USER_PROMPT_TEMPLATE.format(
        name=product.name or "Unknown Product",
        category=product.category or "General",
        price=product.price or 0.0,
        currency=product.currency or "THB",
        description=product.description or "Great product",
        language=language,
        content_mode=content_mode,
        feedback_context=feedback_context
    )

    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        content_json = response.choices[0].message.content
        return json.loads(content_json)
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {e}")
        return _generate_smart_mock(product, language, content_mode)

async def generate_variants(product: Product, language: str = "Thai") -> List[Dict]:
    """
    Generates multiple variations (A/B testing) for a product concurrently.
    """
    modes = ["soft_sell", "hard_sell", "problem_solution"]
    tasks = [generate_content(product, language, mode) for mode in modes]

    results = await asyncio.gather(*tasks)

    variants = []
    for mode, content in zip(modes, results):
        content["content_mode"] = mode
        content["variant_name"] = f"Variant: {mode.replace('_', ' ').title()}"
        variants.append(content)

    return variants

def _generate_smart_mock(product: Product, language: str, content_mode: str) -> Dict[str, str]:
    is_thai = language.lower() in ["thai", "th", "ไทย"]

    # Simple logic to adapt mock based on mode and language
    if is_thai:
        if content_mode == "hard_sell":
            hook = f"ลดแรงมาก! รีบกดด่วนก่อน {product.name} หมดสต็อก!"
            caption = f"🔥 โปรเดือด! {product.name} เหลือแค่ {product.price} {product.currency}! ไม่ซื้อตอนนี้จะเสียใจ! 👇"
        elif content_mode == "problem_solution":
            hook = f"เบื่อไหมกับปัญหาเดิมๆ? ให้ {product.name} ช่วยคุณสิ!"
            caption = f"💡 แก้ปัญหาได้ตรงจุดด้วย {product.name} ใครใช้ก็บอกว่าจึ้ง ในราคาเพียง {product.price} {product.currency}!👇"
        else: # soft_sell
            hook = f"วันนี้ขอมาป้ายยา {product.name} ที่ใช้แล้วชอบมาก"
            caption = f"✨ ไอเทมลูกรักตัวใหม่ {product.name} ใช้งานง่ายสุดๆ ราคาเบาๆ {product.price} {product.currency} ลองไปดูกันน้า 👇"

        video_script = f"1. (0-3s) โชว์สินค้า {product.name} ทันทีพร้อมคำพูดดึงดูด\\n2. (3-10s) สาธิตวิธีใช้หรือจุดเด่น\\n3. (10-15s) ชี้ไปที่ตะกร้าเหลือง"
        cta = "คลิกที่ลิงก์ใน Bio หรือตะกร้าด้านล่างเพื่อซื้อเลย!"
        hashtags = f"#{product.name.replace(' ', '') if product.name else 'ของดี'} #TikTokShop #รีวิว #ป้ายยา"
    else:
        if content_mode == "hard_sell":
            hook = f"FLASH SALE! Get the {product.name} before it's gone!"
            caption = f"🚨 Massive drop! Get your {product.name} for just {product.price} {product.currency}! Stock is running low!👇"
        elif content_mode == "problem_solution":
            hook = f"Tired of the same old struggles? The {product.name} is the answer."
            caption = f"💡 Stop struggling and try the {product.name}. It changed my life and it's only {product.price} {product.currency}!👇"
        else: # soft_sell
            hook = f"I've been loving this {product.name} lately, here's why."
            caption = f"✨ My new favorite daily essential: {product.name}. So easy to use and totally worth {product.price} {product.currency}. Check it out!👇"

        video_script = f"1. (0-3s) Show {product.name} immediately with a hook.\\n2. (3-10s) Demonstrate usage or key features.\\n3. (10-15s) Point to the yellow basket or link."
        cta = "Click the link in Bio or the basket below to get yours now!"
        hashtags = f"#{product.name.replace(' ', '') if product.name else 'MustHave'} #TikTokShop #Review"

    return {
        "hook": hook,
        "caption": caption,
        "video_script": video_script,
        "cta": cta,
        "hashtags": hashtags
    }
