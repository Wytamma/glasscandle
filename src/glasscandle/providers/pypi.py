"""PyPI provider for checking Python package versions."""

from dataclasses import dataclass
from typing import Callable, Optional
import requests


@dataclass
class PyPIProvider:
    """
    PyPI provider for checking Python package versions.

    Attributes:
      name (str): The name of the PyPI provider.
      on_change (Optional[Callable[[str, str, str], None]]): Optional callback function for when a version changes.
    """
    name: str = "pypi"
    on_change: Optional[Callable[[str, str, str], None]] = None

    def key(self, item: str) -> str:
        """
        Returns a key for the given item.

        Args:
          item (str): The item to generate a key for.

        Returns:
          str: The key generated for the item.
        """
        return f"{self.name}::{item}"

    def url_for(self, item: str) -> str:
        """
        Returns the URL for the given item on PyPI.

        Args:
          item (str): The item to get the URL for.

        Returns:
          str: The URL for the item on PyPI.
        """
        return f"https://pypi.org/pypi/{item}/json"

    def fetch_version(self, item: str, session: requests.Session) -> str:
        """
        Fetches the version of the given item from PyPI.

        Args:
          item (str): The item to fetch the version for.
          session (requests.Session): The requests session to use for fetching.

        Returns:
          str: The version of the item fetched from PyPI.

        Raises:
          ValueError: If the item is not found on PyPI, if the URL returns a non-200 status code, or if no version is found in the PyPI response for the item.
        """
        # Use the official JSON API instead of scraping HTML
        from ..http import HTTP_TIMEOUT
        
        url = self.url_for(item)
        r = session.get(url, timeout=HTTP_TIMEOUT)
        if r.status_code == 404:
            raise ValueError(f"{item} not found on PyPI")
        if r.status_code != 200:
            raise ValueError(f"{url} returned {r.status_code}")
        data = r.json()
        version = data.get("info", {}).get("version", "")
        if not version:
            raise ValueError(f"No version in PyPI response for {item}")
        return version
