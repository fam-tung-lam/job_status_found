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


def test_cors_lets_a_local_origin_send_a_credentialed_json_post(client: TestClient) -> None:
    # Given: a page on a local development port about to send a JSON POST with
    # its cookies.
    origin = "http://localhost:53123"

    # When: the browser asks permission first.
    response = client.options(
        "/v1/auth/sign-up",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    # Then: the browser may send it with credentials and read the answer.
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == origin
    assert response.headers["access-control-allow-credentials"] == "true"
