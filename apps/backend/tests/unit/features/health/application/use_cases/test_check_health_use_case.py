from job_status_found.features.health.application.use_cases.check_health_use_case import (
    CheckHealthUseCase,
)


def test_check_health_use_case_succeeds_for_a_running_process() -> None:
    # Given: a health-check use case for a running process.
    check_health_use_case = CheckHealthUseCase()

    # When: the use case runs.
    result = check_health_use_case.invoke()

    # Then: it returns without raising.
    assert result is None
