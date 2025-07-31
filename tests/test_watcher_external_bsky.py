import pytest
import requests
from glasscandle.notifications.bsky import send_bsky_post


@pytest.fixture
def mock_env_variables(monkeypatch):
    monkeypatch.setenv("BSKY_USERNAME", "test_username")
    monkeypatch.setenv("BSKY_PASSWORD", "test_password")


def test_send_bsky_post_success(mock_env_variables, requests_mock):
    # Mock the session creation endpoint
    requests_mock.post("https://bsky.social/xrpc/com.atproto.server.createSession", 
                      json={"accessJwt": "mock_jwt", "did": "mock_did"})
    # Mock the post creation endpoint
    requests_mock.post("https://bsky.social/xrpc/com.atproto.repo.createRecord", 
                      json={"uri": "at://mock_uri", "cid": "mock_cid"})
    
    title = "Test Title"
    content = "Test Content"
    url = "https://example.com"

    # This should not raise an exception
    send_bsky_post(title, content, url)


def test_send_bsky_post_no_content(mock_env_variables, requests_mock):
    # Mock the session creation endpoint
    requests_mock.post("https://bsky.social/xrpc/com.atproto.server.createSession", 
                      json={"accessJwt": "mock_jwt", "did": "mock_did"})
    # Mock the post creation endpoint
    requests_mock.post("https://bsky.social/xrpc/com.atproto.repo.createRecord", 
                      json={"uri": "at://mock_uri", "cid": "mock_cid"})
    
    title = "Test Title"

    # This should not raise an exception
    send_bsky_post(title)


def test_send_bsky_post_long_text(mock_env_variables, requests_mock):
    # Mock the session creation endpoint
    requests_mock.post("https://bsky.social/xrpc/com.atproto.server.createSession", 
                      json={"accessJwt": "mock_jwt", "did": "mock_did"})
    # Mock the post creation endpoint
    requests_mock.post("https://bsky.social/xrpc/com.atproto.repo.createRecord", 
                      json={"uri": "at://mock_uri", "cid": "mock_cid"})
    
    title = "A" * 301

    # This should not raise an exception
    send_bsky_post(title)


def test_send_bsky_post_missing_credentials():
    with pytest.raises(ValueError):
        send_bsky_post("Test Title")

    with pytest.raises(ValueError):
        send_bsky_post("Test Title", username="test_username")

    with pytest.raises(ValueError):
        send_bsky_post("Test Title", password="test_password")


def test_send_bsky_post_request_exception(mock_env_variables, monkeypatch):
    def mock_post(*args, **kwargs):
        raise requests.RequestException("Mocked Request Exception")

    monkeypatch.setattr("requests.post", mock_post)

    with pytest.raises(requests.RequestException):
        send_bsky_post("Test Title")


def test_send_bsky_post_unexpected_error(monkeypatch):
    def mock_post(*args, **kwargs):
        raise Exception("Mocked Unexpected Error")

    monkeypatch.setattr("requests.post", mock_post)

    with pytest.raises(Exception):
        send_bsky_post("Test Title")
