"""Verification codes from the operating system's secure random source."""

import secrets

_VERIFICATION_CODE_DIGITS = 6
"""Digits in a verification code, so one of a million values."""


class SecureRandomVerificationCodeGenerator:
    """`VerificationCodeGenerator` on Python's `secrets` module."""

    def generate_verification_code(self) -> str:
        """Create a new verification code.

        Returns:
            Six decimal digits, each value from `000000` to `999999` equally likely.
        """
        return f"{secrets.randbelow(10**_VERIFICATION_CODE_DIGITS):0{_VERIFICATION_CODE_DIGITS}d}"
