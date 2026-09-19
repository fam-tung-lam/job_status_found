"""An email address and the form that identifies its mailbox."""

import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EmailAddress:
    """An email address whose syntax the caller has already validated."""

    value: str
    """The address as the user typed it; used for display and delivery."""

    @property
    def normalized(self) -> str:
        """The NFKC, lower-case form; addresses with the same form reach one account."""
        return unicodedata.normalize("NFKC", self.value).lower()
