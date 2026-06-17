"""Authentication tests."""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "app" in data


def test_login_invalid():
    response = client.post("/api/auth/login", json={
        "username": "nonexistent",
        "password": "wrong",
    })
    assert response.status_code == 401
