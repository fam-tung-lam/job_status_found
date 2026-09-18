"""Mapped tables of the auth schema; importing this package registers all eight."""

# Sibling-relative imports: the longest absolute module path here exceeds the
# line limit, and the formatter cannot wrap a module path.
from .auth_event_table import AuthEventTable
from .email_challenge_table import EmailChallengeTable
from .external_identity_table import ExternalIdentityTable
from .oauth_authorization_attempt_table import OAuthAuthorizationAttemptTable
from .password_credential_table import PasswordCredentialTable
from .refresh_token_table import RefreshTokenTable
from .session_table import SessionTable
from .user_table import UserTable

__all__ = [
    "AuthEventTable",
    "EmailChallengeTable",
    "ExternalIdentityTable",
    "OAuthAuthorizationAttemptTable",
    "PasswordCredentialTable",
    "RefreshTokenTable",
    "SessionTable",
    "UserTable",
]
