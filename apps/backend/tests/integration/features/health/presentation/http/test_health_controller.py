from fastapi.testclient import TestClient


def test_health_reports_ok(client: TestClient) -> None:
    # Given: the assembled application is running behind the test client.
    health_path = "/health"

    # When: a caller requests the health endpoint.
    response = client.get(health_path)

    # Then: the service answers that it is alive.
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
