"""Auth emails, delivered through the shared SMTP client."""

import logging
from datetime import timedelta

from job_status_found.features.core import EmailDeliveryFailure, SmtpEmailSenderClient

logger = logging.getLogger(__name__)


class SmtpAuthEmailSender:
    """`AuthEmailSender` that writes auth emails and delivers them through the SMTP client."""

    def __init__(self, client: SmtpEmailSenderClient) -> None:
        """Deliver through the shared SMTP client.

        Args:
            client: The client that sends each email.
        """
        self._client = client

    async def send_verification_code(self, recipient: str, code: str, valid_for: timedelta) -> None:
        """Send a code that proves control of the recipient's mailbox.

        Args:
            recipient: The address to deliver to.
            code: The 6-digit code in the clear.
            valid_for: How long the code works, stated in the email.
        """
        minutes = round(valid_for.total_seconds() / 60)
        await self._send(
            "verification code",
            recipient,
            subject=f"{code} is your JSV verification code",
            body=(
                f"Your JSV verification code is {code}.\n\n"
                f"Enter it in the app within {minutes} minutes to finish creating your account.\n\n"
                "If you did not sign up for JSV, you can ignore this email. Without the code, "
                "no account is created for your address.\n"
            ),
        )

    async def send_existing_account_notice(self, recipient: str) -> None:
        """Tell the recipient that someone tried to sign up with their address.

        Args:
            recipient: The address of the existing account.
        """
        await self._send(
            "existing-account notice",
            recipient,
            subject="You already have a JSV account",
            body=(
                "Someone, maybe you, tried to create a JSV account with this email address.\n\n"
                "You already have an account, so nothing changed. To get in, sign in with "
                'your email. If you forgot your password, choose "Forgot your password?" on '
                "the sign-in page.\n\n"
                "If this was not you, you can ignore this email. Your account and password "
                "stay the same.\n"
            ),
        )

    async def _send(self, kind: str, recipient: str, *, subject: str, body: str) -> None:
        """Deliver one auth email, logging a failed delivery instead of raising it.

        Args:
            kind: What the email is, such as `verification code`, for the log.
            recipient: The address to deliver to.
            subject: The subject line.
            body: The plain-text body.
        """
        try:
            await self._client.send(recipient=recipient, subject=subject, body=body)
        except EmailDeliveryFailure as failure:
            # The person asks for a new email instead; the failure names no
            # recipient, and its traceback could, so it is not logged.
            logger.error("Could not send the %s email: %s", kind, failure)
