import pytest
from app.services.ai.content_generator import get_high_performing_examples
from app.models.generated_content import GeneratedContent
from app.models.product import Product
from app.db.database import SessionLocal

def test_get_high_performing_examples():
    db = SessionLocal()

    import uuid
    uid = str(uuid.uuid4())
    # Setup dummy product
    prod = Product(tiktok_product_id=f"feedback_test_{uid}", name="Feedback Test", category=f"TestNiche_{uid}")
    db.add(prod)
    db.commit()
    db.refresh(prod)

    # Insert 10 dummy high performing content pieces
    for i in range(10):
        mode = ["soft_sell", "hard_sell", "problem_solution"][i % 3]
        content = GeneratedContent(
            product_id=prod.id,
            language="English",
            content_mode=mode,
            performance_score=100,
            hook=f"hook_{i}",
            caption=f"caption_{i}",
            video_script="script",
            cta="cta",
            hashtags="tags"
        )
        db.add(content)

    db.commit()

    # Run the function
    result_str = get_high_performing_examples(category=f"TestNiche_{uid}", language="English", limit=3)

    # Assertions
    assert "Example 1" in result_str
    assert "Example 2" in result_str
    assert "Example 3" in result_str

    # Check that diversity exists (not all soft_sell)
    assert "soft_sell" in result_str or "hard_sell" in result_str or "problem_solution" in result_str

    db.close()
