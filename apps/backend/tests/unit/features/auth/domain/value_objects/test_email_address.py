"""Unit tests of the `EmailAddress` value object."""

from job_status_found.features.auth.domain.value_objects.email_address import EmailAddress


def test_addresses_that_differ_in_case_or_unicode_form_share_one_normalized_form() -> None:
    # Given: an address typed with a full-width J and E and mixed case.
    typed = "\uff2aane.Doe@\uff25xample.COM"

    # When: the address is normalized.
    address = EmailAddress(typed)

    # Then: NFKC and lower case give the plain form, and the typed form stays.
    assert address.normalized == "jane.doe@example.com"
    assert address.value == typed
