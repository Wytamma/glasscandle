import pytest
from glasscandle.providers.conda import CondaProvider
import requests


@pytest.fixture
def conda_provider():
    """Default conda provider with default channels."""
    return CondaProvider()


@pytest.fixture
def conda_provider_custom_channels():
    """Conda provider with custom channels."""
    return CondaProvider(channels=["bioconda", "conda-forge"])


@pytest.fixture
def conda_provider_single_channel():
    """Conda provider with single channel."""
    return CondaProvider(channels=["bioconda"])


class TestCondaProviderInit:
    """Test conda provider initialization."""
    
    def test_default_channels(self):
        provider = CondaProvider()
        assert provider.channels == ["conda-forge", "bioconda"]
        assert provider.name == "conda"
    
    def test_custom_channels(self):
        provider = CondaProvider(channels=["bioconda", "custom"])
        assert provider.channels == ["bioconda", "custom"]
    
    def test_single_channel(self):
        provider = CondaProvider(channels=["bioconda"])
        assert provider.channels == ["bioconda"]


class TestCondaProviderKey:
    """Test key generation."""
    
    def test_key_simple_package(self, conda_provider):
        assert conda_provider.key("samtools") == "conda::samtools"
    
    def test_key_with_channel_prefix(self, conda_provider):
        assert conda_provider.key("bioconda::samtools") == "conda::samtools"
    
    def test_key_complex_package_name(self, conda_provider):
        assert conda_provider.key("python-package-name") == "conda::python-package-name"


class TestCondaProviderParsePackageSpec:
    """Test package specification parsing."""
    
    def test_parse_simple_package(self, conda_provider):
        name, channels = conda_provider.parse_package_spec("samtools")
        assert name == "samtools"
        assert channels == ["conda-forge", "bioconda"]
    
    def test_parse_channel_prefix(self, conda_provider):
        name, channels = conda_provider.parse_package_spec("bioconda::samtools")
        assert name == "samtools"
        assert channels == ["bioconda"]
    
    def test_parse_custom_channels(self, conda_provider_custom_channels):
        name, channels = conda_provider_custom_channels.parse_package_spec("numpy")
        assert name == "numpy"
        assert channels == ["bioconda", "conda-forge"]
    
    def test_parse_complex_package_name(self, conda_provider):
        name, channels = conda_provider.parse_package_spec("python-package-name")
        assert name == "python-package-name"
        assert channels == ["conda-forge", "bioconda"]
    
    def test_parse_channel_prefix_complex(self, conda_provider):
        name, channels = conda_provider.parse_package_spec("conda-forge::python-package")
        assert name == "python-package"
        assert channels == ["conda-forge"]


class TestCondaProviderUrlFor:
    """Test URL generation."""
    
    def test_url_for_bioconda(self, conda_provider):
        url = conda_provider.url_for("samtools", "bioconda")
        assert url == "https://api.anaconda.org/package/bioconda/samtools"
    
    def test_url_for_conda_forge(self, conda_provider):
        url = conda_provider.url_for("numpy", "conda-forge")
        assert url == "https://api.anaconda.org/package/conda-forge/numpy"
    
    def test_url_for_custom_channel(self, conda_provider):
        url = conda_provider.url_for("mypackage", "mychannel")
        assert url == "https://api.anaconda.org/package/mychannel/mypackage"
    
    def test_url_for_with_channel_prefix_in_name(self, conda_provider):
        # Should extract just the package name
        url = conda_provider.url_for("bioconda::samtools", "conda-forge")
        assert url == "https://api.anaconda.org/package/conda-forge/samtools"


class TestCondaProviderFetchVersion:
    """Test version fetching with mocked requests."""
    
    def test_fetch_version_found_first_channel(self, conda_provider, requests_mock):
        """Test successful fetch from first channel."""
        requests_mock.get(
            "https://api.anaconda.org/package/conda-forge/numpy",
            json={"latest_version": "1.21.0"},
        )
        requests_mock.get(
            "https://api.anaconda.org/package/bioconda/numpy",
            status_code=404
        )
        
        version = conda_provider.fetch_version("numpy", requests.Session())
        assert version == "1.21.0"
    
    def test_fetch_version_found_second_channel(self, conda_provider, requests_mock):
        """Test successful fetch from second channel after first fails."""
        requests_mock.get(
            "https://api.anaconda.org/package/conda-forge/samtools",
            status_code=404
        )
        requests_mock.get(
            "https://api.anaconda.org/package/bioconda/samtools",
            json={"latest_version": "1.17"},
        )
        
        version = conda_provider.fetch_version("samtools", requests.Session())
        assert version == "1.17"
    
    def test_fetch_version_with_versions_fallback(self, conda_provider, requests_mock):
        """Test fallback to versions list when latest_version is not available."""
        requests_mock.get(
            "https://api.anaconda.org/package/conda-forge/testpkg",
            json={"versions": ["1.0.0", "1.1.0", "1.2.0"]},
        )
        
        version = conda_provider.fetch_version("testpkg", requests.Session())
        assert version == "1.2.0"  # max of versions
    
    def test_fetch_version_channel_prefix(self, conda_provider, requests_mock):
        """Test fetch with channel prefix in package name."""
        requests_mock.get(
            "https://api.anaconda.org/package/bioconda/samtools",
            json={"latest_version": "1.17"},
        )
        
        version = conda_provider.fetch_version("bioconda::samtools", requests.Session())
        assert version == "1.17"
    
    def test_fetch_version_not_found_any_channel(self, conda_provider, requests_mock):
        """Test package not found in any channel."""
        requests_mock.get(
            "https://api.anaconda.org/package/conda-forge/nonexistent",
            status_code=404
        )
        requests_mock.get(
            "https://api.anaconda.org/package/bioconda/nonexistent",
            status_code=404
        )
        
        with pytest.raises(ValueError, match="nonexistent not found in any of the channels"):
            conda_provider.fetch_version("nonexistent", requests.Session())
    
    def test_fetch_version_http_error(self, conda_provider, requests_mock):
        """Test HTTP error handling."""
        requests_mock.get(
            "https://api.anaconda.org/package/conda-forge/errorpkg",
            status_code=500
        )
        requests_mock.get(
            "https://api.anaconda.org/package/bioconda/errorpkg",
            status_code=404
        )
        
        with pytest.raises(ValueError, match="errorpkg not found in any of the channels"):
            conda_provider.fetch_version("errorpkg", requests.Session())
    
    def test_fetch_version_no_versions_available(self, conda_provider, requests_mock):
        """Test when package exists but has no versions."""
        requests_mock.get(
            "https://api.anaconda.org/package/conda-forge/emptypkg",
            json={"versions": []},
        )
        requests_mock.get(
            "https://api.anaconda.org/package/bioconda/emptypkg",
            status_code=404
        )
        
        with pytest.raises(ValueError, match="emptypkg not found in any of the channels"):
            conda_provider.fetch_version("emptypkg", requests.Session())
    
    def test_fetch_version_single_channel(self, conda_provider_single_channel, requests_mock):
        """Test fetch with single channel provider."""
        requests_mock.get(
            "https://api.anaconda.org/package/bioconda/samtools",
            json={"latest_version": "1.17"},
        )
        
        version = conda_provider_single_channel.fetch_version("samtools", requests.Session())
        assert version == "1.17"
    
    def test_fetch_version_json_decode_error(self, conda_provider, requests_mock):
        """Test handling of invalid JSON response."""
        requests_mock.get(
            "https://api.anaconda.org/package/conda-forge/badjson",
            text="invalid json"
        )
        requests_mock.get(
            "https://api.anaconda.org/package/bioconda/badjson",
            status_code=404
        )
        
        with pytest.raises(ValueError, match="badjson not found in any of the channels"):
            conda_provider.fetch_version("badjson", requests.Session())
    
    def test_fetch_version_request_exception(self, conda_provider, requests_mock):
        """Test handling of request exceptions."""
        def connection_error(request, context):
            raise requests.exceptions.ConnectionError("Connection failed")
        
        requests_mock.get(
            "https://api.anaconda.org/package/conda-forge/connection_error",
            text=connection_error
        )
        requests_mock.get(
            "https://api.anaconda.org/package/bioconda/connection_error",
            status_code=404
        )
        
        with pytest.raises(ValueError, match="connection_error not found in any of the channels"):
            conda_provider.fetch_version("connection_error", requests.Session())


class TestCondaProviderIntegration:
    """Integration tests for conda provider."""
    
    def test_multiple_packages_same_provider(self, conda_provider, requests_mock):
        """Test multiple packages with same provider instance."""
        # Setup mocks for different packages
        requests_mock.get(
            "https://api.anaconda.org/package/conda-forge/numpy",
            json={"latest_version": "1.21.0"},
        )
        requests_mock.get(
            "https://api.anaconda.org/package/bioconda/samtools",
            json={"latest_version": "1.17"},
        )
        requests_mock.get(
            "https://api.anaconda.org/package/conda-forge/samtools",
            status_code=404
        )
        
        session = requests.Session()
        
        numpy_version = conda_provider.fetch_version("numpy", session)
        samtools_version = conda_provider.fetch_version("samtools", session)
        
        assert numpy_version == "1.21.0"
        assert samtools_version == "1.17"
    
    def test_provider_with_on_change_callback(self):
        """Test provider with on_change callback."""
        called_args = []
        
        def test_callback(key, old, new):
            called_args.append((key, old, new))
        
        provider = CondaProvider(on_change=test_callback)
        assert provider.on_change == test_callback
    
    def test_custom_name_provider(self):
        """Test provider with custom name."""
        provider = CondaProvider(name="my-conda")
        assert provider.name == "my-conda"
        assert provider.key("samtools") == "my-conda::samtools"


class TestCondaProviderVersionConstraints:
    """Test conda provider with version constraints."""
    
    def test_conda_provider_with_version_constraint(self):
        """Test CondaProvider with version constraint."""
        provider = CondaProvider(version_constraint=">=1.15,<2.0")
        assert provider.version_constraint == ">=1.15,<2.0"
    
    def test_fetch_version_with_constraint_match(self, requests_mock):
        """Test fetch version with constraint that matches available versions."""
        provider = CondaProvider(channels=["bioconda"], version_constraint=">=1.15,<2.0")
        
        requests_mock.get(
            "https://api.anaconda.org/package/bioconda/samtools",
            json={
                "versions": ["1.10", "1.15", "1.16", "1.17", "2.0", "2.1"],
                "latest_version": "2.1"
            },
        )
        
        version = provider.fetch_version("samtools", requests.Session())
        assert version == "1.17"  # Latest version that matches constraint
    
    def test_fetch_version_with_constraint_no_match(self, requests_mock):
        """Test fetch version with constraint that matches no available versions."""
        provider = CondaProvider(channels=["bioconda"], version_constraint=">=3.0")
        
        requests_mock.get(
            "https://api.anaconda.org/package/bioconda/samtools",
            json={
                "versions": ["1.10", "1.15", "1.16", "1.17", "2.0", "2.1"],
                "latest_version": "2.1"
            },
        )
        
        with pytest.raises(ValueError, match="No versions for samtools.*match constraint"):
            provider.fetch_version("samtools", requests.Session())
    
    def test_fetch_version_invalid_constraint(self):
        """Test fetch version with invalid version constraint."""
        provider = CondaProvider(version_constraint="invalid>=1.0")
        
        with pytest.raises(ValueError, match="Invalid version constraint"):
            provider.fetch_version("samtools", requests.Session())
    
    def test_fetch_version_no_constraint(self, requests_mock):
        """Test fetch version without constraint uses latest_version."""
        provider = CondaProvider(channels=["bioconda"])
        
        requests_mock.get(
            "https://api.anaconda.org/package/bioconda/samtools",
            json={
                "versions": ["1.10", "1.15", "1.16", "1.17"],
                "latest_version": "1.17"
            },
        )
        
        version = provider.fetch_version("samtools", requests.Session())
        assert version == "1.17"
