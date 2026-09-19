"""Unit tests of the version 1 pre-normalization email request type."""

from typing import Any

import pytest
from pydantic import BaseModel, ValidationError

from job_status_found.features.auth.presentation.http.v1.schemas.confirm_email_verification_request import (  # noqa: E501
    ConfirmEmailVerificationRequest,
)
from job_status_found.features.auth.presentation.http.v1.schemas.password_sign_in_request import (
    PasswordSignInRequest,
)
from job_status_found.features.auth.presentation.http.v1.schemas.resend_email_verification_request import (  # noqa: E501
    ResendEmailVerificationRequest,
)
from job_status_found.features.auth.presentation.http.v1.schemas.sign_up_request import (
    SignUpRequest,
)

_FULL_WIDTH_J_EMAIL = chr(0xFF4A) + "ane@example.com"
"""An address whose first character NFKC folds to the ASCII letter `j`."""


@pytest.mark.parametrize(
    ("schema", "body"),
    [
        (
            SignUpRequest,
            {
                "first_name": "Jane",
                "last_name": "Doe",
                "email": _FULL_WIDTH_J_EMAIL,
                "password": "matching password",
            },
        ),
        (
            ConfirmEmailVerificationRequest,
            {
                "email": _FULL_WIDTH_J_EMAIL,
                "code": "123456",
                "password": "matching password",
                "client_kind": "web",
                "remember_me": False,
            },
        ),
        (ResendEmailVerificationRequest, {"email": _FULL_WIDTH_J_EMAIL}),
        (
            PasswordSignInRequest,
            {
                "email": _FULL_WIDTH_J_EMAIL,
                "password": "matching password",
                "client_kind": "ios",
                "remember_me": True,
            },
        ),
    ],
    ids=["sign-up", "confirm", "resend", "sign-in"],
)
def test_every_public_email_body_rejects_nfkc_compatibility_text_before_email_normalization(
    schema: type[BaseModel], body: dict[str, Any]
) -> None:
    """
    Given: a public auth body whose raw email contains a full-width character.
    When: the endpoint schema validates it.
    Then: the shared pre-validator refuses the email before `EmailStr` can normalize it.
    """
    # Given: a public auth body whose raw email contains a full-width character.
    # When: the endpoint schema validates it.
    with pytest.raises(ValidationError) as refusal:
        schema.model_validate(body)

    # Then: the shared pre-validator refuses the email field.
    assert [error["loc"] for error in refusal.value.errors()] == [("email",)]
