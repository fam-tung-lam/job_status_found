"""Failures of password sign-in."""


class PasswordSignInFailure(Exception):
    """A password sign-in did not open a session."""


class PasswordSignInInvalidCredentials(PasswordSignInFailure):
    """The email and password do not identify a password account."""

    def __init__(self) -> None:
        """Describe the deliberately non-specific credential failure."""
        super().__init__("The email or password is incorrect.")


class PasswordSignInEmailNotVerified(PasswordSignInFailure):
    """The password is right but the mailbox is not verified."""

    def __init__(self) -> None:
        """Tell the client to continue through email verification."""
        super().__init__("Verify the email address before signing in.")


class PasswordSignInAccountUnavailable(PasswordSignInFailure):
    """The password is right but the account cannot sign in."""

    def __init__(self) -> None:
        """Describe an unavailable account without naming its state."""
        super().__init__("The account is unavailable.")
