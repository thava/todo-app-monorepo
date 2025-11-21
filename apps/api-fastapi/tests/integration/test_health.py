"""Integration tests for health endpoints."""

from fastapi.testclient import TestClient


class TestHealth:
    """Test health endpoints."""

    def test_health_check(self, client: TestClient) -> None:
        """Test GET /health."""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data

    def test_readiness_check(self, client: TestClient) -> None:
        """Test GET /readiness."""
        response = client.get("/readiness")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data
        assert "checks" in data
        assert data["checks"]["database"] == "ok"
