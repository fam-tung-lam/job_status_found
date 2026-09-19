"""Unit tests of the `PasswordPolicy` value object."""

import pytest

from job_status_found.features.auth.domain.value_objects.password_policy import PasswordPolicy

FOUR_BYTE_CHARACTER = "🔒"
"""Four bytes in UTF-8 but one code point.

A policy that counted bytes would accept 11 of them and refuse 128.
"""


@pytest.mark.parametrize(
    ("code_points", "expected_is_allowed"),
    [(11, False), (12, True), (128, True), (129, False)],
)
def test_password_length_is_bounded_by_code_points_not_bytes(
    code_points: int, expected_is_allowed: bool
) -> None:
    # Given: the default policy of 12 to 128 code points, and a password of
    # multi-byte characters.
    policy = PasswordPolicy(min_length=12)
    password = FOUR_BYTE_CHARACTER * code_points

    # When: the policy judges the password.
    is_allowed = policy.is_length_allowed(password)

    # Then: only lengths inside both bounds pass.
    assert is_allowed is expected_is_allowed
