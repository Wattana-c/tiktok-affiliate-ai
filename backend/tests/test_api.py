from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base, get_db
from app.main import app

# Setup test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_tiktok_affiliate_v2.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome to TikTok Affiliate AI" in response.json()["message"]

def test_create_and_read_account():
    import uuid
    uid = str(uuid.uuid4())
    acc_name = f"test_acc_{uid}"
    response = client.post(
        "/api/v1/accounts/",
        json={"platform": "tiktok", "account_name": acc_name, "access_token": "token123", "is_active": True}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["account_name"] == acc_name

    response = client.get("/api/v1/accounts/")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_queue_endpoints():
    response = client.get("/api/v1/queue/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_performance_update():
    from app.models.post_queue import PostQueue
    from app.models.generated_content import GeneratedContent
    from app.models.product import Product
    from app.models.account import Account

    db = TestingSessionLocal()

    # Setup dummy data
    import uuid
    uid = str(uuid.uuid4())
    prod = Product(tiktok_product_id=f"test1_{uid}", name="Test", price=100.0)
    db.add(prod)
    db.commit()
    db.refresh(prod)

    cont = GeneratedContent(product_id=prod.id, language="Thai", hook="test", caption="test", video_script="test", cta="test", hashtags="test")
    db.add(cont)
    db.commit()
    db.refresh(cont)

    acc = Account(platform="tiktok", account_name=f"test_{uid}", access_token="test")
    db.add(acc)
    db.commit()
    db.refresh(acc)

    q = PostQueue(product_id=prod.id, account_id=acc.id, content_id=cont.id, status="posted")
    db.add(q)
    db.commit()
    db.refresh(q)

    # Put performance
    response = client.put(
        f"/api/v1/queue/{q.id}/performance",
        json={"views": 100, "clicks": 50, "conversions": 10, "likes": 200, "revenue": 150.0}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["views"] == 100
    assert data["conversions"] == 10
    assert data["revenue"] == 150.0

    # Verify AI feedback score logic
    db.refresh(cont)
    assert cont.performance_score > 0

    # Verify shadowban logic (views < 10 triggers it, we set to 100 so it should be false)
    db.refresh(acc)
    assert acc.is_shadowbanned == False

    # Verify dynamic cost and account profit calculation
    db.refresh(q)
    assert q.dynamic_cost > 0.0
    assert acc.total_profit == q.profit_score

    # Test Negative Revenue Validation (422 expected)
    response_neg = client.put(
        f"/api/v1/queue/{q.id}/performance",
        json={"revenue": -5.0}
    )
    assert response_neg.status_code == 422

    # Test High Revenue Anomaly Logic (Should still pass 200 but trigger logger)
    response_high = client.put(
        f"/api/v1/queue/{q.id}/performance",
        json={"views": 50, "conversions": 10, "revenue": 15000.0}
    )
    assert response_high.status_code == 200
    db.refresh(q)
    assert q.error_message is not None
    assert "Anomaly detected" in q.error_message

    # Test Conversions > Views Validation (422 expected)
    response_conv = client.put(
        f"/api/v1/queue/{q.id}/performance",
        json={"views": 10, "conversions": 50}
    )
    assert response_conv.status_code == 422

    db.close()
