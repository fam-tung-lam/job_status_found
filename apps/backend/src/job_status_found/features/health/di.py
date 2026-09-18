"""Dependency providers that assemble the health feature."""

from job_status_found.features.health.application.use_cases.check_health_use_case import (
    CheckHealthUseCase,
)


def get_check_health_use_case() -> CheckHealthUseCase:
    """Provide the health check use case.

    Returns:
        A new `CheckHealthUseCase`.
    """
    return CheckHealthUseCase()
