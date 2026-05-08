import json
import os
import asyncio
import logging
from typing import Dict, List
from openai import AsyncOpenAI
from app.schemas.product import Product
from app.services.ai.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
import logging

logger = logging.getLogger(__name__)

openai_api_key = os.getenv("OPENAI_API_KEY")
google_api_key = os.getenv("GOOGLE_API_KEY")

openai_client = AsyncOpenAI(api_key=openai_api_key) if openai_api_key else None

if google_api_key:
    gemini_client = genai.Client(api_key=google_api_key)
else:
    gemini_client = None


def get_high_performing_examples(category: str, language: str, limit: int = 3) -> str:
    """Fetches high performing content from the DB to use as examples in the prompt."""
    import random
    db = SessionLocal()
    try:
        # Fetch the latest 50 high performing samples across diverse modes
        query = db.query(GeneratedContent).join(DBProduct).filter(
            GeneratedContent.language == language,
            GeneratedContent.performance_score > 50
        )

        # Don't strictly filter by exact category to ensure cross-pollination of viral mechanics
        # Just order by the newest/best and fetch a larger pool
        pool = query.order_by(GeneratedContent.created_at.desc(), GeneratedContent.performance_score.desc()).limit(50).all()

        if not pool:
            return ""

        # Randomly drop 20% of the pool to ensure structural diversity and prevent overfitting
        pool_size = len(pool)
        drop_count = int(pool_size * 0.2)
        if drop_count > 0 and pool_size > drop_count:
            sampled_pool = random.sample(pool, pool_size - drop_count)
        else:
            sampled_pool = pool

        # Ensure diversity by picking items with different content_modes if possible
        selected_examples = []
        seen_modes = set()

        # Priority to matching category if available in the sampled pool
        category_matches = [p for p in sampled_pool if p.product.category == category]
        random.shuffle(category_matches)

        for content in category_matches:
            if content.content_mode not in seen_modes:
                selected_examples.append(content)
                seen_modes.add(content.content_mode)
            if len(selected_examples) >= limit:
                break

        # Fill the rest with general viral structures if we haven't hit the limit
        if len(selected_examples) < limit:
            random.shuffle(sampled_pool)
            for content in sampled_pool:
                if content not in selected_examples and content.content_mode not in seen_modes:
                    selected_examples.append(content)
                    seen_modes.add(content.content_mode)
                if len(selected_examples) >= limit:
                    break

        # Fallback fill if modes were extremely limited
        if len(selected_examples) < limit:
            for content in sampled_pool:
                if content not in selected_examples:
                    selected_examples.append(content)
                if len(selected_examples) >= limit:
                    break

        examples_str = ""
        for idx, content in enumerate(selected_examples):
            examples_str += f"\nExample {idx+1} ({content.content_mode}):\n"
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
    Generates AI affiliate content using Gemini or OpenAI for a specific mode.
    Falls back to smart mock if no API key is provided.
    """
    if not gemini_client and not openai_client:
        logger.warning(f"No AI API keys found. Falling back to smart mocks ({content_mode}).")
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
        if gemini_client:
            # Use Google Gemini (New SDK)
            full_prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}\n\nReturn the result in JSON format."
            response = await gemini_client.aio.models.generate_content(
                model='gemini-2.5-flash-lite',

                contents=full_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type='application/json',
                )
            )
            return json.loads(response.text)
        else:
            # Use OpenAI
            response = await openai_client.chat.completions.create(
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
        logger.error(f"Error calling AI API: {e}")
        return _generate_smart_mock(product, language, content_mode)



async def generate_variants(product: Product, language: str = "Thai") -> List[Dict]:
    """
    Generates multiple variations (A/B testing) for a product concurrently.
    Uses 80/20 Exploration vs Exploitation strategy based on ContentStrategyMetrics.
    """
    import random
    from app.models.content_strategy_metrics import ContentStrategyMetrics

    # Base modes available
    all_modes = ["soft_sell", "hard_sell", "problem_solution", "storytelling", "urgent_flash"]

    # Anti-Overfitting AI:
    # 1. Fetch best performing mode (Exploitation) and apply diversity penalty.
    best_mode = "soft_sell" # default
    diversity_penalty = 0
    db = SessionLocal()
    try:
        best_metric = db.query(ContentStrategyMetrics).filter(
            ContentStrategyMetrics.metric_type == "content_mode"
        ).order_by(ContentStrategyMetrics.average_score.desc()).first()
        if best_metric:
            best_mode = best_metric.metric_value

            # Simple diversity penalty logic: if total_uses is very high, temporarily suppress it
            if best_metric.total_uses > 100:
                best_mode = random.choice([m for m in all_modes if m != best_metric.metric_value])
                diversity_penalty = 1

    finally:
        db.close()

    modes_to_generate = []

    # 2. Decide Strategy (80% Exploit Best, 20% Explore Wildcard)
    # Variant 1: Exploitation (best mode)
    modes_to_generate.append(best_mode)

    # Variant 2 & 3: Mix of Exploit or Explore
    for _ in range(2):
        if random.random() < 0.8:
            # 80% chance to exploit
            modes_to_generate.append(best_mode if best_mode in all_modes else "soft_sell")
        else:
            # 20% chance to explore wild-card or experimental mode
            modes_to_generate.append("wildcard_explore")

    # Ensure some uniqueness if we just duplicated best_mode 3 times
    modes_to_generate = list(set(modes_to_generate))
    if len(modes_to_generate) < 3:
        for m in all_modes:
            if m not in modes_to_generate:
                modes_to_generate.append(m)
            if len(modes_to_generate) >= 3:
                break

    modes_to_generate = modes_to_generate[:3]
    tasks = [generate_content(product, language, mode) for mode in modes_to_generate]

    results = await asyncio.gather(*tasks)

    variants = []
    for mode, content in zip(modes_to_generate, results):
        content["content_mode"] = mode
        content["variant_name"] = f"Variant: {mode.replace('_', ' ').title()}"
        content["diversity_penalty"] = diversity_penalty
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
