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
    response = client.post(
        "/api/v1/accounts/",
        json={"platform": "tiktok", "account_name": "test_acc", "access_token": "token123", "is_active": True}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["account_name"] == "test_acc"

    response = client.get("/api/v1/accounts/")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_queue_endpoints():
    response = client.get("/api/v1/queue/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
