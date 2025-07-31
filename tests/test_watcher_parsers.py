import pytest
from glasscandle.parsers import etag, last_modified, sha256_of_body, regex, jsonpath
import requests


@pytest.fixture
def mock_response():
    class MockResponse:
        def __init__(self, headers, content, text):
            self.headers = headers
            self.content = content
            self.text = text

    return MockResponse(
        headers={"ETag": 'W/"123456"'}, content=b"test content", text="test content"
    )


def test_etag(mock_response):
    assert etag(mock_response) == "123456"


def test_last_modified(mock_response):
    with pytest.raises(ValueError, match="No Last-Modified header"):
        last_modified(mock_response)


def test_sha256_of_body(mock_response):
    assert (
        sha256_of_body(mock_response)
        == "6ae8a75555209fd6c44157c0aed8016e763ff435a19cf186f76863140143ff72"
    )


def test_regex():
    class MockResponse:
        def __init__(self):
            self.headers = {"Content-Type": "text/plain"}
            self.text = "abc123def"
    
    res = MockResponse()
    assert regex("abc(\\d+)def")(res) == "123"


def test_jsonpath():
    res = requests.Response()
    res._content = b'{"key": "value"}'
    assert jsonpath("$.key")(res) == "value"
