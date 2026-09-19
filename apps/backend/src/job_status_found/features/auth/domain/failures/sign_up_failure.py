"""Why a sign-up is refused.

A sign-up for an email that already has an account is not a failure: it
succeeds like any other, so the answer never reveals which emails have accounts.
"""


class SignUpFailure(Exception):
    """Base of every reason a sign-up is refused."""


class SignUpPasswordTooWeak(SignUpFailure):
    """The password is shorter or longer than the password policy allows."""

    def __init__(self, *, min_length: int, max_length: int) -> None:
        """Record the bounds the password missed.

        Args:
            min_length: Fewest Unicode code points the policy allows.
            max_length: Most Unicode code points the policy allows.
        """
        super().__init__(f"The password must have {min_length} to {max_length} characters.")
        self.min_length = min_length
        self.max_length = max_length
