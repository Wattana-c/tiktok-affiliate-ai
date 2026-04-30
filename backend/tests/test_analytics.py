from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_analytics_endpoints():
    response = client.get("/api/v1/analytics/dashboard-stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_conversions" in data

    response2 = client.get("/api/v1/analytics/top-styles")
    assert response2.status_code == 200
    assert isinstance(response2.json(), list)
