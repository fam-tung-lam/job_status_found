"""Check whether the service can serve requests."""

from job_status_found.features.health.application.dtos.health_status import HealthStatus


class CheckHealth:
    """Report the liveness of the running process."""

    def execute(self) -> HealthStatus:
        """Report that the process is alive.

        Returns:
            A status that is always `"ok"`.
        """
        return HealthStatus(status="ok")
