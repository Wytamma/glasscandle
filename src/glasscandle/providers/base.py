"""Base provider protocol and constants."""

from typing import Protocol
import requests


class Provider(Protocol):
    """Protocol for version checking providers."""
    name: str

    def key(self, item: str) -> str:
        """Return the DB key for this provider + item."""
        ...

    def url_for(self, item: str) -> str:
        """Return the canonical lookup URL for this item."""
        ...

    def fetch_version(self, item: str, session: requests.Session) -> str:
        """Return the current version string, or raise ValueError on not found."""
        ...
