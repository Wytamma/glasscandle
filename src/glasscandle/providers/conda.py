"""Conda provider for checking conda package versions across multiple channels."""

from dataclasses import dataclass
from typing import Callable, Optional, List, Tuple
import requests


@dataclass
class CondaProvider:
    """
    Conda provider for checking conda package versions across multiple channels.

    Attributes:
        name (str): The name of the provider. Default is "conda".
        channels (List[str]): List of conda channels to search. Default is ["conda-forge", "bioconda"].
        version_constraint (Optional[str]): Version constraint string (e.g., ">=1.21,<2").
        on_change (Optional[Callable[[str, str, str], None]]): Optional callback function to be called on change.

    Methods:
        key(item: str) -> str:
            Returns the key for the given item.

        parse_package_spec(item: str) -> Tuple[str, List[str]]:
            Parse package specification to extract package name and channels.
            
            Supports formats:
            - "package_name" -> uses default channels
            - "channel::package_name" -> uses specified channel only
            
        url_for(item: str, channel: str) -> str:
            Returns the URL for the given item in the specified channel.

        fetch_version(item: str, session: requests.Session) -> str:
            Fetches the version of the given item from conda channels.
            
            Searches channels in order until package is found.

    Examples:
        >>> provider = CondaProvider()
        >>> version = provider.fetch_version("samtools", requests.Session())
        "1.17"
        
        >>> provider = CondaProvider(channels=["bioconda"], version_constraint=">=1.15,<2")
        >>> version = provider.fetch_version("blast", requests.Session())
        "1.17"  # Only if version matches constraint
    """
    name: str = "conda"
    channels: List[str] = None
    version_constraint: Optional[str] = None
    on_change: Optional[Callable[[str, str, str], None]] = None

    def __post_init__(self):
        if self.channels is None:
            self.channels = ["conda-forge", "bioconda"]

    def key(self, item: str) -> str:
        """Generate database key for the package."""
        package_name, _ = self.parse_package_spec(item)
        return f"{self.name}::{package_name}"

    def parse_package_spec(self, item: str) -> Tuple[str, List[str]]:
        """
        Parse package specification to extract package name and channels.
        
        Args:
            item: Package specification (e.g., "samtools", "bioconda::samtools")
            
        Returns:
            Tuple of (package_name, channels_to_search)
        """
        if "::" in item:
            channel, package_name = item.split("::", 1)
            return package_name, [channel]
        else:
            return item, self.channels

    def url_for(self, item: str, channel: str) -> str:
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

    def fetch_version(self, item: str, session: requests.Session) -> str:
        """
        Fetch the latest version of a conda package.
        
        Searches through channels in order until package is found.
        Applies version constraints if specified.
        
        Args:
            item: Package specification
            session: HTTP session for requests
            
        Returns:
            Latest version string that matches constraints
            
        Raises:
            ValueError: If package not found in any channel or no version matches constraints
        """
        from ..http import HTTP_TIMEOUT
        from ..version_constraints import VersionConstraint
        
        package_name, channels_to_search = self.parse_package_spec(item)
        
        # Initialize version constraint if specified
        constraint = None
        if self.version_constraint:
            try:
                constraint = VersionConstraint(self.version_constraint)
            except Exception as e:
                raise ValueError(f"Invalid version constraint '{self.version_constraint}': {e}")
        
        last_error = None
        for channel in channels_to_search:
            try:
                url = self.url_for(package_name, channel)
                r = session.get(url, timeout=HTTP_TIMEOUT)
                
                if r.status_code == 404:
                    last_error = f"{package_name} not found in channel {channel}"
                    continue
                    
                if r.status_code != 200:
                    last_error = f"{url} returned {r.status_code}"
                    continue
                
                data = r.json()
                
                # Get all available versions
                all_versions = data.get("versions") or []
                if not all_versions:
                    # If no versions list, try latest_version
                    latest = data.get("latest_version")
                    if latest:
                        all_versions = [latest]
                
                if not all_versions:
                    last_error = f"No versions for {package_name} in channel {channel}"
                    continue
                
                # Apply version constraints if specified
                if constraint:
                    valid_version = constraint.get_latest_valid(all_versions)
                    if valid_version:
                        return valid_version
                    else:
                        last_error = f"No versions for {package_name} in channel {channel} match constraint '{self.version_constraint}'"
                        continue
                else:
                    # No constraints, return latest version
                    latest_version = data.get("latest_version")
                    if latest_version:
                        return latest_version
                    else:
                        # Fall back to max of versions if latest_version not available
                        return max(all_versions)
                
            except Exception as e:
                last_error = f"Error fetching {package_name} from {channel}: {e}"
                continue
        
        # If we get here, package wasn't found in any channel or no versions matched constraints
        channels_str = ", ".join(channels_to_search)
        constraint_str = f" matching constraint '{self.version_constraint}'" if self.version_constraint else ""
        raise ValueError(f"{package_name} not found{constraint_str} in any of the channels: {channels_str}. Last error: {last_error}")
