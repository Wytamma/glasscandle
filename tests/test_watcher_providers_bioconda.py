import pytest
from glasscandle.providers.bioconda import BiocondaProvider
import requests


@pytest.fixture
def bioconda_provider():
    return BiocondaProvider()


def test_key(bioconda_provider):
    assert bioconda_provider.key("test") == "bioconda::test"


def test_url_for(bioconda_provider):
    assert (
        bioconda_provider.url_for("test")
        == "https://api.anaconda.org/package/bioconda/test"
    )


def test_fetch_version_found(bioconda_provider, requests_mock):
    requests_mock.get(
        "https://api.anaconda.org/package/bioconda/test",
        json={"latest_version": "1.0.0"},
    )
    version = bioconda_provider.fetch_version("test", requests.Session())
    assert version == "1.0.0"


def test_fetch_version_not_found(bioconda_provider, requests_mock):
    requests_mock.get("https://api.anaconda.org/package/bioconda/test", status_code=404)
    with pytest.raises(ValueError):
        bioconda_provider.fetch_version("test", requests.Session())


def test_fetch_version_error(bioconda_provider, requests_mock):
    requests_mock.get("https://api.anaconda.org/package/bioconda/test", status_code=500)
    with pytest.raises(ValueError):
        bioconda_provider.fetch_version("test", requests.Session())


def test_fetch_version_no_versions(bioconda_provider, requests_mock):
    requests_mock.get(
        "https://api.anaconda.org/package/bioconda/test", json={"versions": []}
    )
    with pytest.raises(ValueError):
        bioconda_provider.fetch_version("test", requests.Session())


def test_bioconda_inherits_conda_behavior(bioconda_provider):
    """Test that BiocondaProvider correctly inherits from CondaProvider."""
    # Test that it's using bioconda channel only
    assert bioconda_provider.channels == ["bioconda"]

    # Test parse_package_spec method is inherited
    name, channels = bioconda_provider.parse_package_spec("samtools")
    assert name == "samtools"
    assert channels == ["bioconda"]

    # Test channel prefix still works
    name, channels = bioconda_provider.parse_package_spec("conda-forge::numpy")
    assert name == "numpy"
    assert channels == ["conda-forge"]


def test_bioconda_url_generation(bioconda_provider):
    """Test URL generation uses conda provider logic."""
    url = bioconda_provider.url_for("samtools", "bioconda")
    assert url == "https://api.anaconda.org/package/bioconda/samtools"


def test_fetch_version_fallback_to_versions(bioconda_provider, requests_mock):
    """Test that BiocondaProvider falls back to versions list when latest_version is not available."""
    requests_mock.get(
        "https://api.anaconda.org/package/bioconda/test",
        json={"versions": ["1.0.0", "1.1.0", "1.2.0"]},
    )
    version = bioconda_provider.fetch_version("test", requests.Session())
    assert version == "1.2.0"
