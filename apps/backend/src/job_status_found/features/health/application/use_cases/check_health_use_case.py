"""Check whether the service can serve requests."""


class CheckHealthUseCase:
    """Check the liveness of the running process."""

    def invoke(self) -> None:
        """Check that the process is alive.

        Returns normally when the process can serve requests. A failed check
        raises instead.
        """
