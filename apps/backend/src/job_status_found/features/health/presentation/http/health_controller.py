"""`GET /health`: report that the process is alive."""

from typing import Annotated

from fastapi import APIRouter, Depends

from job_status_found.features.health.application.use_cases.check_health_use_case import (
    CheckHealthUseCase,
)
from job_status_found.features.health.di import get_check_health_use_case
from job_status_found.features.health.presentation.http.schemas.health_status_response import (
    HealthStatusResponse,
)

router = APIRouter()


@router.get("/health")
def check_health(
    check_health_use_case: Annotated[CheckHealthUseCase, Depends(get_check_health_use_case)],
) -> HealthStatusResponse:
    """Report that the process is alive.

    Args:
        check_health_use_case: The health check use case.

    Returns:
        A status that is always `"ok"`.
    """
    check_health_use_case.invoke()
    return HealthStatusResponse(status="ok")
