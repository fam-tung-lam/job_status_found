from fastapi.testclient import TestClient


def test_cors_allows_a_local_development_origin(client: TestClient) -> None:
    # Given: a browser page served from a local development port.
    origin = "http://localhost:53123"

    # When: the page requests the health endpoint.
    response = client.get("/health", headers={"Origin": origin})

    # Then: the browser is allowed to read the response.
    assert response.headers["access-control-allow-origin"] == origin


def test_cors_rejects_a_foreign_origin(client: TestClient) -> None:
    # Given: a browser page served from a site outside local development.
    origin = "https://example.com"

    # When: the page requests the health endpoint.
    response = client.get("/health", headers={"Origin": origin})

    # Then: the browser is not allowed to read the response.
    assert "access-control-allow-origin" not in response.headers
