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
      version_constraint (Optional[str]): Version constraint string (e.g., ">=1.21,<2").
      on_change (Optional[Callable[[str, str, str], None]]): Optional callback function for when a version changes.
    """
    name: str = "pypi"
    version_constraint: Optional[str] = None
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
        
        Applies version constraints if specified.

        Args:
          item (str): The item to fetch the version for.
          session (requests.Session): The requests session to use for fetching.

        Returns:
          str: The latest version of the item that matches constraints.

        Raises:
          ValueError: If the item is not found on PyPI, if the URL returns a non-200 status code,
                     if no version is found in the PyPI response for the item, or if no version
                     matches the specified constraints.
        """
        # Use the official JSON API instead of scraping HTML
        from ..http import HTTP_TIMEOUT
        from ..version_constraints import VersionConstraint
        
        url = self.url_for(item)
        r = session.get(url, timeout=HTTP_TIMEOUT)
        if r.status_code == 404:
            raise ValueError(f"{item} not found on PyPI")
        if r.status_code != 200:
            raise ValueError(f"{url} returned {r.status_code}")
        
        data = r.json()
        
        # Apply version constraints if specified
        if self.version_constraint:
            try:
                constraint = VersionConstraint(self.version_constraint)
                # Get all available versions from releases
                all_versions = list(data.get("releases", {}).keys())
                if not all_versions:
                    raise ValueError(f"No versions found in PyPI response for {item}")
                
                # Find the latest version that matches constraints
                valid_version = constraint.get_latest_valid(all_versions)
                if valid_version:
                    return valid_version
                else:
                    raise ValueError(f"No versions for {item} on PyPI match constraint '{self.version_constraint}'")
            except Exception as e:
                if "Invalid version constraint" in str(e):
                    raise e
                raise ValueError(f"Error applying version constraint for {item}: {e}")
        else:
            # No constraints, return latest version
            version = data.get("info", {}).get("version", "")
            if not version:
                raise ValueError(f"No version in PyPI response for {item}")
            return version
