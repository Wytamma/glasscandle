import pytest
from glasscandle.providers.pypi import PyPIProvider
import requests


@pytest.fixture
def pypi_provider():
    return PyPIProvider()


def test_key(pypi_provider):
    assert pypi_provider.key("requests") == "pypi::requests"


def test_url_for(pypi_provider):
    assert pypi_provider.url_for("requests") == "https://pypi.org/pypi/requests/json"


def test_fetch_version_found(pypi_provider, requests_mock):
    requests_mock.get(
        "https://pypi.org/pypi/requests/json", json={"info": {"version": "2.25.1"}}
    )
    version = pypi_provider.fetch_version("requests", requests.Session())
    assert version == "2.25.1"


def test_fetch_version_not_found(pypi_provider, requests_mock):
    requests_mock.get("https://pypi.org/pypi/invalid_package/json", status_code=404)
    with pytest.raises(ValueError):
        pypi_provider.fetch_version("invalid_package", requests.Session())


def test_fetch_version_non_200_status(pypi_provider, requests_mock):
    requests_mock.get("https://pypi.org/pypi/invalid_package/json", status_code=500)
    with pytest.raises(ValueError):
        pypi_provider.fetch_version("invalid_package", requests.Session())


def test_fetch_version_no_version(pypi_provider, requests_mock):
    requests_mock.get("https://pypi.org/pypi/invalid_package/json", json={"info": {}})
    with pytest.raises(ValueError):
        pypi_provider.fetch_version("invalid_package", requests.Session())
