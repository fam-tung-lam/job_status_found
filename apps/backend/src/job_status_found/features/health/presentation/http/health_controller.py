"""Unversioned health endpoint."""

from typing import Annotated

from fastapi import APIRouter, Depends

from job_status_found.features.health.application.dtos.health_status import HealthStatus
from job_status_found.features.health.application.use_cases.check_health import CheckHealth
from job_status_found.features.health.di import get_check_health

router = APIRouter(tags=["health"])


@router.get("/health")
def health(check_health: Annotated[CheckHealth, Depends(get_check_health)]) -> HealthStatus:
    """Report that the process is alive.

    Args:
        check_health: The health check use case.

    Returns:
        A status that is always `"ok"`.
    """
    return check_health.execute()
