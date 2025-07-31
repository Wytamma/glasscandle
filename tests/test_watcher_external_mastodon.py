import pytest
from glasscandle.notifications.mastodon import send_mastodon_post, toot


@pytest.fixture
def mock_env_variables(monkeypatch):
    monkeypatch.setenv("MASTODON_ACCESS_TOKEN", "mock_access_token")
    monkeypatch.setenv("MASTODON_API_BASE_URL", "mock_api_base_url")


def test_send_mastodon_post(mock_env_variables, mocker):
    # Mock the Mastodon class at the module level where it's imported
    mock_mastodon_class = mocker.patch("mastodon.Mastodon")
    mock_mastodon_instance = mock_mastodon_class.return_value
    
    # Test with all parameters provided
    send_mastodon_post(
        "Test Title",
        "Test Content",
        "https://example.com",
        "mock_access_token",
        "mock_api_base_url",
    )
    
    # Verify Mastodon was initialized correctly
    mock_mastodon_class.assert_called_once_with(
        access_token="mock_access_token",
        api_base_url="mock_api_base_url",
    )
    # Verify toot was called
    mock_mastodon_instance.toot.assert_called_once()


def test_send_mastodon_post_with_env_vars(mock_env_variables, mocker):
    # Mock the Mastodon class
    mock_mastodon_class = mocker.patch("mastodon.Mastodon")
    
    # Test with only required parameters (should use env vars)
    send_mastodon_post("Test Title")
    
    # Verify it used env vars
    mock_mastodon_class.assert_called_with(
        access_token="mock_access_token",
        api_base_url="mock_api_base_url",
    )


def test_send_mastodon_post_missing_credentials(mocker):
    # Mock the Mastodon class
    mocker.patch("mastodon.Mastodon")
    
    # Test with missing access token and no env var
    with pytest.raises(ValueError, match="access token must be provided"):
        send_mastodon_post("Test Title", access_token=None, api_base_url="http://example.com")

    # Test with missing API base URL and no env var  
    with pytest.raises(ValueError, match="API base URL must be provided"):
        send_mastodon_post("Test Title", access_token="token", api_base_url=None)


def test_toot(mocker):
    # Mock the Mastodon class at the module level where it's imported
    mock_mastodon_class = mocker.patch("mastodon.Mastodon")
    mock_mastodon_instance = mock_mastodon_class.return_value
    
    # Test with all parameters provided
    toot("mock_access_token", "mock_api_base_url", "Test Toot")
    
    # Verify Mastodon was initialized correctly
    mock_mastodon_class.assert_called_once_with(
        access_token="mock_access_token",
        api_base_url="mock_api_base_url",
    )
    # Verify toot was called
    mock_mastodon_instance.toot.assert_called_once_with("Test Toot")

    # Test with text exceeding 499 characters (should be truncated)
    mock_mastodon_class.reset_mock()
    mock_mastodon_instance.reset_mock()
    
    long_text = "a" * 501
    toot("mock_access_token", "mock_api_base_url", long_text)
    
    # Verify toot was called with truncated text
    mock_mastodon_instance.toot.assert_called_once_with("a" * 499)
