"""
Smoke tests for API endpoint availability.
Run with: pytest tests/test_endpoints.py -v
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Tests for health and general endpoints that require no authentication."""

    def test_health_check(self):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "message" in data

    def test_root_api(self):
        response = client.get("/api")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Dietik App API is running"

    def test_test_endpoint(self):
        response = client.get("/api/test")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Test endpoint working"
        assert data["status"] == "success"

    def test_config_endpoint(self):
        response = client.get("/api/config")
        assert response.status_code == 200
        data = response.json()
        assert "api_base_url" in data
        assert "app_name" in data
        assert "app_version" in data


class TestProtectedEndpointsRequireAuth:
    """Verify that protected endpoints reject unauthenticated requests."""

    @pytest.mark.parametrize("method,path", [
        ("GET", "/api/user/profile"),
        ("GET", "/api/body-dimensions"),
        ("GET", "/api/meals"),
        ("GET", "/api/meals/frequent"),
        ("GET", "/api/nutritional-plans"),
        ("GET", "/api/dashboard"),
        ("GET", "/api/products/search?q=test"),
    ])
    def test_protected_endpoint_returns_401(self, method, path):
        response = client.request(method, path)
        assert response.status_code in (401, 403), (
            f"{method} {path} returned {response.status_code}, expected 401/403"
        )
