import pytest
from glasscandle.providers.url import URLProvider
import requests


@pytest.fixture
def url_provider():
    return URLProvider()


def test_key(url_provider):
    assert url_provider.key("https://www.example.com") == "url::https://www.example.com"


def test_url_for(url_provider):
    assert url_provider.url_for("https://www.example.com") == "https://www.example.com"


def test_validate_allowed_domain(url_provider):
    url_provider.allowed_domains = ("example.com",)
    with pytest.raises(ValueError):
        url_provider._validate("https://www.google.com")


def test_fetch_version(requests_mock, url_provider):
    url = "https://www.example.com"
    requests_mock.head(url, status_code=200)
    requests_mock.get(url, text="Test content")

    session = requests.Session()
    version = url_provider.fetch_version(url, session)

    assert version == "Test content"


def test_fetch_version_http_not_allowed(url_provider):
    url_provider.allow_http = False
    with pytest.raises(ValueError):
        url_provider.fetch_version("http://www.example.com", requests.Session())


def test_fetch_version_unsupported_scheme(url_provider):
    with pytest.raises(ValueError):
        url_provider.fetch_version("ftp://www.example.com", requests.Session())


def test_fetch_version_response_too_large(requests_mock, url_provider):
    url = "https://www.example.com"
    requests_mock.head(url, headers={"Content-Length": "2000000"})

    session = requests.Session()
    with pytest.raises(ValueError):
        url_provider.fetch_version(url, session)


def test_fetch_version_parser_returns_empty_string(requests_mock, url_provider):
    url = "https://www.example.com"
    requests_mock.head(url, status_code=200)
    requests_mock.get(url, text="")

    session = requests.Session()
    with pytest.raises(ValueError):
        url_provider.fetch_version(url, session)
