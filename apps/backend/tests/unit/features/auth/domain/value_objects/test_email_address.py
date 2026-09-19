"""Unit tests of the `EmailAddress` value object."""

from job_status_found.features.auth.domain.value_objects.email_address import EmailAddress


class TestEmailAddress:
    """The normalized form `EmailAddress` gives a typed address."""

    def test_addresses_that_differ_in_case_or_unicode_form_share_one_normalized_form(
        self,
    ) -> None:
        """
        Given: an address typed with full-width letters and mixed case.
        When: the address is normalized.
        Then: its normalized form is plain lower case, and its typed form is kept.
        """
        # Given: an address typed with a full-width J and E and mixed case.
        typed_address = "\uff2aane.Doe@\uff25xample.COM"

        # When: the address is normalized.
        address = EmailAddress(typed_address)

        # Then: NFKC and lower case give the plain form, and the typed form stays.
        assert address.normalized == "jane.doe@example.com"
        assert address.as_typed == typed_address
