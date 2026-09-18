from job_status_found.features.health.application.dtos.health_status import HealthStatus
from job_status_found.features.health.application.use_cases.check_health import CheckHealth


def test_check_health_reports_ok() -> None:
    # Given: a health-check use case for a running process.
    check_health = CheckHealth()

    # When: the use case runs.
    health_status = check_health.execute()

    # Then: it reports the process as alive.
    assert health_status == HealthStatus(status="ok")
