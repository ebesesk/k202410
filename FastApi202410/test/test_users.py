# tests/api/test_users.py
from fastapi.testclient import TestClient
from k202410.main import app

client = TestClient(app)

def test_login():
    response = client.post("/api/v1/users/login", data={"username": "testuser", "password": "password123"})
    assert response.status_code == 200
    assert "access_token" in response.json()
