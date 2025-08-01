"""Conda-forge provider for checking conda package versions."""

from dataclasses import dataclass
from typing import Callable, Optional
from .conda import CondaProvider


@dataclass
class CondaForgeProvider(CondaProvider):
    """
    Conda-forge provider for checking conda package versions.
    
    This is a specialized version of CondaProvider that only searches the conda-forge channel
    and provides a convenient interface for conda-forge packages.

    Attributes:
      name (str): The name of the provider. Default is "condaforge".
      on_change (Optional[Callable[[str, str, str], None]]): Optional callback function to be called on change.

    Methods:
      key(item: str) -> str:
        Returns the key for the given item.

        Args:
          item (str): The item to generate the key for.

        Returns:
          str: The key for the item.

      fetch_version(item: str, session: requests.Session) -> str:
        Fetches the version of the given item from conda-forge.

        Args:
          item (str): The item to fetch the version for.
          session (requests.Session): The requests session to use for fetching.

        Raises:
          ValueError: If the item is not found, URL returns an error, or no versions are available.

        Returns:
          str: The version of the item.

        Notes:
          - Picks the latest version by string comparison of 'latest_version' if present, otherwise falls back to max of 'versions'.

        Examples:
          >>> provider = CondaForgeProvider()
          >>> version = provider.fetch_version("package_name", requests.Session())
          "1.0.0"
    """

    name: str = "condaforge"
    version_constraint: Optional[str] = None
    on_change: Optional[Callable[[str, str, str], None]] = None

    def __post_init__(self):
        # Override parent's __post_init__ to set channels to conda-forge only
        self.channels = ["conda-forge"]

    def key(self, item: str) -> str:
        """Generate database key maintaining backward compatibility."""
        package_name, _ = self.parse_package_spec(item)
        return f"{self.name}::{package_name}"
    
    def url_for(self, item: str, channel: str = "conda-forge") -> str:
        """
        Generate API URL for package in specific channel.
        
        Args:
            item: Package name
            channel: Conda channel name
            
        Returns:
            API URL for the package in the channel
        """
        package_name, _ = self.parse_package_spec(item)
        return f"https://api.anaconda.org/package/{channel}/{package_name}"
