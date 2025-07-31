"""URL provider for checking arbitrary URLs with custom parsers."""

from dataclasses import dataclass
from typing import Callable, Optional, Tuple
from urllib.parse import urlparse
import requests


MAX_BYTES = 1_000_000  # 1 MB cap for safety


@dataclass
class URLProvider:
    """
    URL provider for checking arbitrary URLs with custom parsers.

    Attributes:
      parse (Optional[Callable[[requests.Response], str]]): Custom parser function for response.
      name (str): Name of the URL provider.
      allow_http (bool): Flag to allow HTTP URLs.
      allowed_domains (Tuple[str, ...]): Tuple of allowed domain names.
      on_change (Optional[Callable[[str, str, str], None]]): Callback function for URL changes.
    """
    parse: Optional[Callable[[requests.Response], str]] = None
    name: str = "url"
    allow_http: bool = False
    allowed_domains: Tuple[str, ...] = ()
    on_change: Optional[Callable[[str, str, str], None]] = None

    def key(self, item: str) -> str:
        """
        Generates a unique key for the given URL.

        Args:
          item (str): The URL for which key is generated.

        Returns:
          str: Unique key for the URL.
        """
        # item is the URL
        return f"{self.name}::{item}"

    def url_for(self, item: str) -> str:
        """
        Returns the URL as is.

        Args:
          item (str): The URL.

        Returns:
          str: The input URL.
        """
        return item

    def _validate(self, url: str) -> None:
        """
        Validates the URL based on scheme, HTTP allowance, and allowed domains.

        Args:
          url (str): The URL to validate.

        Raises:
          ValueError: If URL scheme is unsupported, plain HTTP is blocked, or domain is not allowed.
        """
        pu = urlparse(url)
        if pu.scheme not in ("https", "http"):
            raise ValueError("Unsupported URL scheme")
        if pu.scheme == "http" and not self.allow_http:
            raise ValueError("Plain HTTP blocked")
        host = pu.hostname or ""
        if self.allowed_domains and host not in self.allowed_domains:
            raise ValueError(f"Domain not allowed: {host}")

    def fetch_version(self, item: str, session: requests.Session) -> str:
        """
        Fetches the version of the given URL using a session.

        Args:
          item (str): The URL to fetch version for.
          session (requests.Session): Session object for making HTTP requests.

        Returns:
          str: Version of the URL content.

        Raises:
          ValueError: If HTTP request fails, response is too large, parser returns empty string, or other validation issues.
        """
        from ..http import HTTP_TIMEOUT
        
        self._validate(item)

        # HEAD probe to avoid huge downloads
        try:
            h = session.head(item, timeout=HTTP_TIMEOUT, allow_redirects=True)
            if h.status_code >= 400 and h.status_code != 405:
                raise ValueError(f"{item} HEAD returned {h.status_code}")
            clen = h.headers.get("Content-Length")
            if clen and int(clen) > MAX_BYTES:
                raise ValueError(f"Response too large: {clen} bytes")
        except requests.RequestException:
            # fall back to GET if HEAD is not supported or fails
            pass

        r = session.get(item, timeout=HTTP_TIMEOUT, stream=False)
        if r.status_code != 200:
            raise ValueError(f"{item} returned {r.status_code}")
        # Optional: enforce size cap even without Content-Length
        if r.headers.get("Content-Length") is None and len(r.content) > MAX_BYTES:
            raise ValueError("Response too large without Content-Length")
        if self.parse is None:
            result = r.text.strip()
        else:
            result = self.parse(r).strip()
        if not result:
            raise ValueError("Parser returned empty string")
        return result
