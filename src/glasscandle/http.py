"""HTTP utilities and session management."""

import requests
from requests.adapters import HTTPAdapter, Retry


HTTP_TIMEOUT = 10  # seconds


def create_session() -> requests.Session:
    """Create a configured requests session with retries."""
    s = requests.Session()
    s.headers.update(
        {
            "User-Agent": "watcher/1.0 (+https://example.org); requests",
            "Accept": "application/json, text/html;q=0.9, */*;q=0.1",
        }
    )
    retries = Retry(
        total=3,
        backoff_factor=0.3,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET", "HEAD"]),
        raise_on_redirect=False,
        raise_on_status=False,
    )
    s.mount("https://", HTTPAdapter(max_retries=retries))
    s.mount("http://", HTTPAdapter(max_retries=retries))
    return s
