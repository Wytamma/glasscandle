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


def test_pypi_provider_with_version_constraint():
    """Test PyPIProvider with version constraint."""
    provider = PyPIProvider(version_constraint=">=2.25,<3.0")
    assert provider.version_constraint == ">=2.25,<3.0"


def test_fetch_version_with_constraint_match(requests_mock):
    """Test fetch version with constraint that matches available versions."""
    provider = PyPIProvider(version_constraint=">=2.25,<3.0")

    requests_mock.get(
        "https://pypi.org/pypi/requests/json",
        json={
            "info": {"version": "3.1.0"},  # Latest version
            "releases": {
                "2.20.0": {},
                "2.25.0": {},
                "2.25.1": {},
                "2.26.0": {},
                "3.0.0": {},
                "3.1.0": {},
            },
        },
    )

    version = provider.fetch_version("requests", requests.Session())
    assert version == "2.26.0"  # Latest version that matches constraint


def test_fetch_version_with_constraint_no_match(requests_mock):
    """Test fetch version with constraint that matches no available versions."""
    provider = PyPIProvider(version_constraint=">=4.0")

    requests_mock.get(
        "https://pypi.org/pypi/requests/json",
        json={
            "info": {"version": "3.1.0"},
            "releases": {
                "2.25.0": {},
                "2.26.0": {},
                "3.0.0": {},
                "3.1.0": {},
            },
        },
    )

    with pytest.raises(ValueError, match="No versions for requests.*match constraint"):
        provider.fetch_version("requests", requests.Session())


def test_fetch_version_constraint_invalid(requests_mock):
    """Test fetch version with invalid constraint."""
    provider = PyPIProvider(version_constraint="invalid>=1.0")

    requests_mock.get(
        "https://pypi.org/pypi/requests/json",
        json={"info": {"version": "3.1.0"}, "releases": {}},
    )

    with pytest.raises(ValueError, match="Invalid version constraint"):
        provider.fetch_version("requests", requests.Session())


def test_fetch_version_no_constraint(requests_mock):
    """Test fetch version without constraint uses latest version from info."""
    provider = PyPIProvider()  # No version constraint

    requests_mock.get(
        "https://pypi.org/pypi/requests/json",
        json={
            "info": {"version": "3.1.0"},
            "releases": {
                "2.25.0": {},
                "3.1.0": {},
            },
        },
    )

    version = provider.fetch_version("requests", requests.Session())
    assert version == "3.1.0"
