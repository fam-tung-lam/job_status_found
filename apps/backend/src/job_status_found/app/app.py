"""Application composition root."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from job_status_found.features.auth.di import open_auth
from job_status_found.features.auth.domain.failures.sign_up_failure import SignUpFailure
from job_status_found.features.auth.presentation.http.auth_exception_handlers import (
    handle_sign_up_failure,
)
from job_status_found.features.auth.presentation.http.auth_router import router as auth_router
from job_status_found.features.core import (
    ProblemDetailsFastAPI,
    get_app_settings,
    handle_request_validation_error,
    open_database,
)
from job_status_found.features.health.presentation.http.health_router import (
    router as health_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Own application-wide resources for the life of the process.

    Acquire shared clients and pools before `yield` and close them after it.

    Args:
        app: The application being started.

    Yields:
        Control to FastAPI while the application serves requests.
    """
    async with open_database(app, get_app_settings().database_url), open_auth(app):
        yield


def create_app() -> FastAPI:
    """Build the FastAPI application with its lifespan and routers.

    Returns:
        A new, fully composed application instance.
    """
    settings = get_app_settings()
    app = ProblemDetailsFastAPI(
        title=settings.app_name, version=settings.version, lifespan=lifespan
    )
    # Credentials let the web app's refresh cookie travel; the origin regex
    # never matches every origin, which credentials would make unsafe.
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=settings.cors_allow_origin_regex,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )
    app.add_exception_handler(RequestValidationError, handle_request_validation_error)
    app.add_exception_handler(SignUpFailure, handle_sign_up_failure)
    app.include_router(health_router)
    app.include_router(auth_router, prefix="/v1")
    return app
