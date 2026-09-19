"""Auth emails sent after the HTTP response."""

from datetime import timedelta

from starlette.background import BackgroundTasks

from job_status_found.features.auth.application.ports.auth_email_sender import AuthEmailSender


class DeferredAuthEmailSender:
    """`AuthEmailSender` that hands each email to the request's background tasks.

    The response leaves before the mail server is contacted, so neither its
    latency nor a failure shows in the response or its timing. An email is
    lost if the process stops before it is sent; the person then asks for a new
    one.
    """

    def __init__(
        self, background_tasks: BackgroundTasks, immediate_sender: AuthEmailSender
    ) -> None:
        """Defer every email to the current request's background tasks.

        Args:
            background_tasks: The tasks that run after the response is sent.
            immediate_sender: The sender that delivers each email as soon as it is called.
        """
        self._background_tasks = background_tasks
        self._immediate_sender = immediate_sender

    async def send_verification_code(self, recipient: str, code: str, valid_for: timedelta) -> None:
        """Schedule a verification code email for after the response.

        Args:
            recipient: The address to deliver to.
            code: The 6-digit code in the clear.
            valid_for: How long the code works, stated in the email.
        """
        self._background_tasks.add_task(
            self._immediate_sender.send_verification_code, recipient, code, valid_for
        )

    async def send_existing_account_notice(self, recipient: str) -> None:
        """Schedule an existing-account notice for after the response.

        Args:
            recipient: The address of the existing account.
        """
        self._background_tasks.add_task(
            self._immediate_sender.send_existing_account_notice, recipient
        )
