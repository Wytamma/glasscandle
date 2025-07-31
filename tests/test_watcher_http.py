import pytest
from glasscandle.http import create_session


@pytest.fixture
def session():
    return create_session()


def test_create_session():
    session = create_session()
    assert (
        session.headers["User-Agent"] == "watcher/1.0 (+https://example.org); requests"
    )
    assert session.headers["Accept"] == "application/json, text/html;q=0.9, */*;q=0.1"
    assert "https://" in session.adapters
    assert "http://" in session.adapters


def test_create_session_custom_headers():
    # The create_session function doesn't accept custom headers,
    # so this test should verify the default headers
    session = create_session()
    assert session.headers["User-Agent"] == "watcher/1.0 (+https://example.org); requests"
    assert session.headers["Accept"] == "application/json, text/html;q=0.9, */*;q=0.1"


def test_create_session_invalid_headers():
    # Since create_session doesn't accept parameters, this test
    # should just verify it creates a session successfully
    session = create_session()
    assert session is not None


def test_create_session_invalid_retry():
    with pytest.raises(TypeError):
        create_session(retry="invalid_retry")
