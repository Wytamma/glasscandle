"""Tests for CondaForgeProvider class."""

import pytest
import requests
from unittest.mock import Mock, patch

from src.glasscandle.providers.condaforge import CondaForgeProvider


class TestCondaForgeProvider:
    """Test CondaForgeProvider class."""

    def test_init_default(self):
        """Test default initialization."""
        provider = CondaForgeProvider()
        assert provider.name == "condaforge"
        assert provider.channels == ["conda-forge"]
        assert provider.version_constraint is None
        assert provider.on_change is None

    def test_init_with_version_constraint(self):
        """Test initialization with version constraint."""
        provider = CondaForgeProvider(version_constraint=">=1.0,<2.0")
        assert provider.version_constraint == ">=1.0,<2.0"
        assert provider.channels == ["conda-forge"]

    def test_key_generation(self):
        """Test database key generation."""
        provider = CondaForgeProvider()
        
        # Simple package name
        assert provider.key("numpy") == "condaforge::numpy"
        
        # Package with channel specification (should be ignored in key)
        assert provider.key("conda-forge::numpy") == "condaforge::numpy"

    def test_url_generation(self):
        """Test URL generation for conda-forge packages."""
        provider = CondaForgeProvider()
        
        # Default channel (conda-forge)
        url = provider.url_for("numpy")
        assert url == "https://api.anaconda.org/package/conda-forge/numpy"
        
        # Explicit channel parameter
        url = provider.url_for("numpy", "conda-forge")
        assert url == "https://api.anaconda.org/package/conda-forge/numpy"

    def test_parse_package_spec(self):
        """Test package specification parsing."""
        provider = CondaForgeProvider()
        
        # Simple package name
        name, channels = provider.parse_package_spec("numpy")
        assert name == "numpy"
        assert channels == ["conda-forge"]
        
        # Package with channel specification
        name, channels = provider.parse_package_spec("some-channel::numpy")
        assert name == "numpy"
        assert channels == ["some-channel"]

    @patch('requests.Session.get')
    def test_fetch_version_success(self, mock_get):
        """Test successful version fetching."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "latest_version": "1.21.0",
            "versions": ["1.20.0", "1.21.0", "1.22.0"]
        }
        mock_get.return_value = mock_response
        
        provider = CondaForgeProvider()
        session = requests.Session()
        
        version = provider.fetch_version("numpy", session)
        assert version == "1.21.0"
        
        # Verify correct URL was called
        mock_get.assert_called_once_with(
            "https://api.anaconda.org/package/conda-forge/numpy",
            timeout=10
        )

    @patch('requests.Session.get')
    def test_fetch_version_with_constraint(self, mock_get):
        """Test version fetching with constraint filtering."""
        # Mock API response with multiple versions
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "versions": ["1.19.0", "1.20.0", "1.21.0", "1.22.0", "2.0.0"]
        }
        mock_get.return_value = mock_response
        
        # Provider with version constraint
        provider = CondaForgeProvider(version_constraint=">=1.20,<2.0")
        session = requests.Session()
        
        version = provider.fetch_version("numpy", session)
        # Should return highest version matching constraint
        assert version == "1.22.0"

    @patch('requests.Session.get')
    def test_fetch_version_no_matching_constraint(self, mock_get):
        """Test version fetching when no versions match constraint."""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "versions": ["0.9.0", "0.9.1"]
        }
        mock_get.return_value = mock_response
        
        # Provider with constraint that matches no versions
        provider = CondaForgeProvider(version_constraint=">=1.0")
        session = requests.Session()
        
        with pytest.raises(ValueError, match="numpy not found matching constraint"):
            provider.fetch_version("numpy", session)

    @patch('requests.Session.get')
    def test_fetch_version_http_error(self, mock_get):
        """Test version fetching with HTTP error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        provider = CondaForgeProvider()
        session = requests.Session()
        
        with pytest.raises(ValueError, match="numpy not found in any of the channels"):
            provider.fetch_version("numpy", session)

    @patch('requests.Session.get')
    def test_fetch_version_no_versions(self, mock_get):
        """Test version fetching when no versions available."""
        # Mock API response with no versions
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response
        
        provider = CondaForgeProvider()
        session = requests.Session()
        
        with pytest.raises(ValueError, match="numpy not found in any of the channels"):
            provider.fetch_version("numpy", session)

    def test_inheritance_from_conda_provider(self):
        """Test that CondaForgeProvider inherits from CondaProvider."""
        provider = CondaForgeProvider()
        
        # Should have all CondaProvider methods
        assert hasattr(provider, 'fetch_version')
        assert hasattr(provider, 'parse_package_spec')
        assert hasattr(provider, 'url_for')
        assert hasattr(provider, 'key')
        
        # Should override channels to conda-forge only
        assert provider.channels == ["conda-forge"]
