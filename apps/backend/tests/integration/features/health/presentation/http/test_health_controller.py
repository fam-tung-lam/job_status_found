from fastapi.testclient import TestClient


def test_health_reports_ok(client: TestClient) -> None:
    # Given: the assembled application is running behind the test client.
    health_path = "/health"

    # When: a caller requests the health endpoint.
    response = client.get(health_path)

    # Then: the service answers that it is alive.
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_openapi_publishes_health_without_version(client: TestClient) -> None:
    # Given: the assembled application is running behind the test client.
    openapi_path = "/openapi.json"

    # When: a caller reads the OpenAPI document.
    paths = client.get(openapi_path).json()["paths"]

    # Then: the unversioned health path is published and the removed version path is not.
    assert "/health" in paths
    assert "/version" not in paths
