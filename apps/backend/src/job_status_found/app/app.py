"""Application composition root."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from job_status_found.app.app_settings import get_settings
from job_status_found.db.db import open_database
from job_status_found.features.health.presentation.http.health_controller import (
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
    async with open_database(app, get_settings().database_url):
        yield


def create_app() -> FastAPI:
    """Build the FastAPI application with its lifespan and routers.

    Returns:
        A new, fully composed application instance.
    """
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version=settings.version, lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=settings.cors_allow_origin_regex,
        allow_methods=["GET"],
    )
    app.include_router(health_router)
    return app
