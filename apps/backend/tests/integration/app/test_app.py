"""API tests of the application-wide middleware that `create_app` installs."""

from fastapi import APIRouter
from fastapi.testclient import TestClient

from job_status_found.app.app import create_app, include_authenticated_feature_router


class TestCreateAppCors:
    """The cross-origin policy of the CORS middleware that `create_app` installs."""

    def test_cors_allows_a_local_development_origin(self, client: TestClient) -> None:
        """
        Given: a browser page served from a local development port.
        When: the page requests the health endpoint.
        Then: the browser may read the response.
        """
        # Given: a browser page served from a local development port.
        origin = "http://localhost:53123"

        # When: the page requests the health endpoint.
        response = client.get("/health", headers={"Origin": origin})

        # Then: the browser is allowed to read the response.
        assert response.headers["access-control-allow-origin"] == origin

    def test_cors_rejects_a_foreign_origin(self, client: TestClient) -> None:
        """
        Given: a browser page served from a site outside local development.
        When: the page requests the health endpoint.
        Then: the browser may not read the response.
        """
        # Given: a browser page served from a site outside local development.
        origin = "https://example.com"

        # When: the page requests the health endpoint.
        response = client.get("/health", headers={"Origin": origin})

        # Then: the browser is not allowed to read the response.
        assert "access-control-allow-origin" not in response.headers

    def test_cors_lets_a_local_origin_send_a_credentialed_json_post(
        self, client: TestClient
    ) -> None:
        """
        Given: a page on a local development port about to send a JSON POST with its cookies.
        When: the browser asks permission first.
        Then: the browser may send the POST with credentials and read the answer.
        """
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


class TestIncludeAuthenticatedFeatureRouter:
    """The authenticated-by-default feature-router composition rule."""

    def test_an_unmarked_feature_route_rejects_an_anonymous_request(self) -> None:
        """
        Given: a feature route with no endpoint-level authentication dependency.
        When: the application includes it through the feature-router helper.
        Then: an anonymous request is rejected with the bearer challenge.
        """
        # Given: a feature route with no endpoint-level authentication dependency.
        router = APIRouter()

        @router.get("/unmarked")
        async def unmarked_route() -> dict[str, bool]:
            """Return success when the composition guard lets the request through."""
            return {"ok": True}

        # When: the application includes it through the feature-router helper.
        app = create_app()
        include_authenticated_feature_router(app, router)
        with TestClient(app) as client:
            response = client.get("/v1/unmarked")

        # Then: an anonymous request is rejected with the bearer challenge.
        assert (response.status_code, response.json()["code"]) == (
            401,
            "access_token_invalid",
        )
        assert response.headers["www-authenticate"] == "Bearer"
