"""Dependency providers that assemble the health feature."""

from job_status_found.features.health.application.use_cases.check_health import CheckHealth


def get_check_health() -> CheckHealth:
    """Provide the health check use case.

    Returns:
        A new `CheckHealth` use case.
    """
    return CheckHealth()
