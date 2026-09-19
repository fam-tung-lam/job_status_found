"""Delivery of auth emails."""

from datetime import timedelta
from typing import Protocol


class AuthEmailSender(Protocol):
    """Delivers auth emails on a best-effort basis.

    Call it only after the transaction that the email describes has committed.
    A delivery failure is logged, never raised: the person asks for a new email
    instead.
    """

    async def send_verification_code(self, recipient: str, code: str, valid_for: timedelta) -> None:
        """Send a code that proves control of the recipient's mailbox.

        Args:
            recipient: The address to deliver to.
            code: The 6-digit code in the clear.
            valid_for: How long the code works, stated in the email.
        """
        ...

    async def send_existing_account_notice(self, recipient: str) -> None:
        """Tell the recipient that someone tried to sign up with their address.

        Args:
            recipient: The address of the existing account.
        """
        ...
