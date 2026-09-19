"""Verification codes from the operating system's secure random source."""

import secrets

_VERIFICATION_CODE_DIGIT_COUNT = 6
"""Digits in a verification code, so one of a million values."""


def generate_verification_code() -> str:
    """Create a new code that proves control of a mailbox.

    Returns:
        Six decimal digits, including leading zeros, each value from `000000`
        to `999999` equally likely.
    """
    random_number = secrets.randbelow(10**_VERIFICATION_CODE_DIGIT_COUNT)
    return f"{random_number:0{_VERIFICATION_CODE_DIGIT_COUNT}d}"
