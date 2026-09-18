"""ASGI entry point for servers such as `uvicorn job_status_found.main:app`."""

from job_status_found.app.app import create_app

app = create_app()
