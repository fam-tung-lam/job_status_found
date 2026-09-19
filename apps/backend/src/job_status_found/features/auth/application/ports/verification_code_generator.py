"""Creation of the 6-digit codes emailed to verify a mailbox."""

from typing import Protocol


class VerificationCodeGenerator(Protocol):
    """Creates verification codes, replaceable so tests know the code."""

    def generate_verification_code(self) -> str:
        """Create a new verification code.

        Returns:
            Six decimal digits, including leading zeros, drawn from a
            cryptographically secure source.
        """
        ...
