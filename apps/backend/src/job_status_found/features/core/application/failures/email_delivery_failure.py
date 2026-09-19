"""Failure raised when the shared email client cannot deliver a message."""


class EmailDeliveryFailure(Exception):
    """The SMTP server could not be reached, or it refused the email.

    The message names the SMTP error but never the recipient, so a caller may
    log it.
    """
