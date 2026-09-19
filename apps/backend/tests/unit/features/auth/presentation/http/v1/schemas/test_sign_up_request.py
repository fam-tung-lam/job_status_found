"""Unit tests of the version 1 `SignUpRequest` body schema."""

import pytest
from pydantic import ValidationError

from job_status_found.features.auth.presentation.http.v1.schemas.sign_up_request import (
    SignUpRequest,
)

VALID_SIGN_UP_BODY = {
    "first_name": "Jane",
    "last_name": "Doe",
    "email": "jane@example.com",
    "password": "correct horse battery",
}
"""A sign-up body that passes validation, for a test to spoil one field of."""


class TestSignUpRequest:
    """The input `SignUpRequest` refuses before it reaches the sign-up."""

    @pytest.mark.parametrize(
        ("field", "value"),
        [
            # PostgreSQL cannot store a NUL byte, so it would fail as a 500.
            ("first_name", "Ja\x00ne"),
            # Normalization would fold it into another mailbox's account.
            ("email", chr(0xFF4A) + "ane@example.com"),  # a full-width j
            # No hash can encode a lone surrogate, so it would fail as a 500.
            ("password", "correct horse \ud800"),
        ],
    )
    def test_input_the_sign_up_cannot_store_safely_is_refused_as_invalid(
        self, field: str, value: str
    ) -> None:
        """
        Given: an otherwise valid body with one field the sign-up cannot store safely.
        When: the body is validated.
        Then: validation refuses exactly that field.
        """
        # Given: an otherwise valid body with one unsafe field.
        body = VALID_SIGN_UP_BODY | {field: value}

        # When: the body is validated.
        with pytest.raises(ValidationError) as refusal:
            SignUpRequest.model_validate(body)

        # Then: exactly that field is refused, which the API answers with a 422.
        assert [error["loc"] for error in refusal.value.errors()] == [(field,)]
