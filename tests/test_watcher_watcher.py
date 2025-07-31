import pytest
from glasscandle.watcher import Watcher


@pytest.fixture
def watcher():
    return Watcher()


def test_init(watcher):
    assert watcher.db is not None
    assert watcher.pool is not None
    assert watcher._session is not None
    assert watcher._allowed_custom_domains == ()
    assert watcher._on_change is None


def test_bioconda(watcher):
    def on_change(key, old_version, new_version):
        pass

    watcher.bioconda("test_package", on_change=on_change)
    assert "test_package" in watcher.pool.bioconda
    assert watcher.pool.bioconda["test_package"].on_change == on_change


def test_pypi(watcher):
    def on_change(key, old_version, new_version):
        pass

    watcher.pypi("test_package", on_change=on_change)
    assert "test_package" in watcher.pool.pypi
    assert watcher.pool.pypi["test_package"].on_change == on_change


def test_url(watcher):
    def parser(response):
        pass

    def on_change(key, old_version, new_version):
        pass

    watcher.url(
        "https://example.com",
        parser=parser,
        allowed_domains=("example.com",),
        on_change=on_change,
    )
    assert "https://example.com" in watcher.pool.url
    assert watcher.pool.url["https://example.com"].on_change == on_change


def test_url_regex(watcher):
    def on_change(key, old_version, new_version):
        pass

    watcher.url_regex(
        "https://example.com", 
        pattern=r"(\d+\.\d+\.\d+)", 
        group=1, 
        on_change=on_change,
        allowed_domains=("example.com",)
    )
    assert "https://example.com" in watcher.pool.url


def test_response(watcher):
    def on_change(key, old_version, new_version):
        pass

    # Configure watcher to allow example.com domain
    watcher._allowed_custom_domains = ("example.com",)

    @watcher.response("https://example.com", on_change=on_change)
    def custom_func(response):
        pass

    assert "https://example.com" in watcher.pool.custom
    assert watcher.pool.custom_callbacks["https://example.com"] == on_change


def test_json(watcher):
    def on_change(key, old_version, new_version):
        pass

    watcher.json("https://example.com", path="$['version']", on_change=on_change, allowed_domains=("example.com",))
    assert "https://example.com" in watcher.pool.url


def test__update(watcher):
    def on_change(key, old_version, new_version):
        pass

    watcher._update("test_key", "1.0.0", on_change=on_change)
    assert watcher.db.get("test_key") == "1.0.0"


def test_run(watcher, monkeypatch):
    # Mock the session.get method to avoid actual network calls
    called_urls = []
    
    def mock_get(url, timeout=None):
        called_urls.append(url)
        # Create a mock response
        class MockResponse:
            status_code = 200
            def json(self):
                return {"version": "1.0.0"}
        return MockResponse()
    
    monkeypatch.setattr(watcher._session, "get", mock_get)
    
    # Add a provider to test
    def dummy_on_change(key, old_version, new_version):
        pass
    watcher.pypi("test_package", on_change=dummy_on_change)
    
    # Run without warnings
    watcher.run(warn=True)  # Use warn=True to avoid exceptions if mocked requests fail


def test_start(watcher, monkeypatch):
    # Mock time.sleep and implement a counter to stop the infinite loop
    sleep_calls = []
    run_calls = []
    
    def mock_sleep(duration):
        sleep_calls.append(duration)
        # Stop after first iteration to prevent infinite loop
        raise KeyboardInterrupt("Test stop")
    
    def mock_run():
        run_calls.append(True)
    
    monkeypatch.setattr("time.sleep", mock_sleep)
    monkeypatch.setattr(watcher, "run", mock_run)
    
    # Should call run once, then sleep, then KeyboardInterrupt stops it
    watcher.start(interval=60)
    
    assert len(run_calls) == 1
    assert len(sleep_calls) == 1
    assert sleep_calls[0] == 60


def test__wrap(watcher):
    d = {"test_key": "test_value"}
    wrapped_d = watcher._wrap(d)
    assert wrapped_d == d
