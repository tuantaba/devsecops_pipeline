from fastapi.testclient import TestClient


def test_get_customer_returns_mock_customer(client: TestClient) -> None:
    response = client.get("/api/v1/customers/cust-001")

    assert response.status_code == 200
    assert response.json() == {
        "id": "cust-001",
        "name": "Acme Corporation",
        "email": "security-contact@acme.example",
        "status": "active",
        "plan": "enterprise",
    }


def test_get_customer_returns_404_for_unknown_customer(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/customers/missing")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "message": "Customer 'missing' was not found",
            "path": "/api/v1/customers/missing",
        }
    }

