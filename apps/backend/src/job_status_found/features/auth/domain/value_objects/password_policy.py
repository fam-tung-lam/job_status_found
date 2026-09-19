"""The rule every new password must meet."""

from dataclasses import dataclass

MAX_PASSWORD_LENGTH = 128
"""Most Unicode code points a password may have."""


@dataclass(frozen=True, slots=True)
class PasswordPolicy:
    """Length bounds for a new password, with no composition rules.

    The breach check is a separate rule that a later operation adds.
    """

    min_length: int
    """Fewest Unicode code points a new password may have."""

    max_length: int = MAX_PASSWORD_LENGTH
    """Most Unicode code points a new password may have."""

    def validate(self, password: str) -> bool:
        """Tell whether a password is long enough and not too long.

        Python's `len` counts code points, not bytes, so an accented letter or
        an emoji counts once.

        Args:
            password: The password in the clear.

        Returns:
            Whether the password's length lies within both bounds.
        """
        return self.min_length <= len(password) <= self.max_length
