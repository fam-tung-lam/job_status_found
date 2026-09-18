"""Health status returned by the health check."""

from typing import Literal

from pydantic import BaseModel, ConfigDict


class HealthStatus(BaseModel):
    """Liveness result of the service."""

    model_config = ConfigDict(
        frozen=True,
        use_attribute_docstrings=True,
        json_schema_extra={"examples": [{"status": "ok"}]},
    )

    status: Literal["ok"]
    """Always `"ok"` when the process can serve requests."""
