import pytest
from glasscandle.providers.base import Provider
import requests


@pytest.fixture
def mock_provider():
    class MockProvider(Provider):
        name = "MockProvider"

        def key(self, item: str) -> str:
            return f"{self.name}_{item}"

        def url_for(self, item: str) -> str:
            return f"https://mockprovider.com/{item}"

        def fetch_version(self, item: str, session: requests.Session) -> str:
            return "1.0.0"

    return MockProvider()


def test_key(mock_provider):
    assert mock_provider.key("test") == "MockProvider_test"


def test_url_for(mock_provider):
    assert mock_provider.url_for("test") == "https://mockprovider.com/test"


def test_fetch_version(mock_provider):
    session = requests.Session()
    assert mock_provider.fetch_version("test", session) == "1.0.0"
