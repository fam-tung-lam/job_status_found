"""How every settings class of the service reads its configuration."""

from pydantic_settings import SettingsConfigDict


def settings_config(env_prefix: str) -> SettingsConfigDict:
    """Configure a settings class the way every settings class of the service reads.

    Values come from the prefixed environment variables, then `.env`. A
    rejected value never reaches an error message, because it may be a secret.
    An empty variable, such as an optional one Compose passes as `${NAME:-}`,
    counts as unset: `.env`, then the default, applies.

    Args:
        env_prefix: The variable prefix, such as `JSF_` or `JSF_AUTH_`.

    Returns:
        The `model_config` of the settings class.
    """
    return SettingsConfigDict(
        env_prefix=env_prefix,
        env_file=".env",
        extra="ignore",
        hide_input_in_errors=True,
        env_ignore_empty=True,
    )
