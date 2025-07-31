import pytest
from glasscandle.notifications import (
    _extract_url_from_key,
    slack_notifier,
    email_notifier,
    mastodon_notifier,
    bsky_notifier,
)


@pytest.mark.parametrize(
    "key, include_url, expected_output",
    [
        ("url::https://example.com", True, "https://example.com"),
        ("pypi::requests", True, "https://pypi.org/project/requests/"),
        ("bioconda::samtools", True, "https://anaconda.org/bioconda/samtools"),
        ("invalid_key", True, None),
        ("url::https://example.com", False, None),
    ],
)
def test_extract_url_from_key(key, include_url, expected_output):
    assert _extract_url_from_key(key, include_url) == expected_output


def test_slack_notifier_missing_webhook_url(monkeypatch):
    monkeypatch.delenv("SLACK_WEBHOOK_URL", raising=False)
    with pytest.raises(ValueError):
        slack_notifier()


def test_email_notifier_missing_config(monkeypatch):
    monkeypatch.setenv("EMAIL_TO", "")
    with pytest.raises(ValueError):
        email_notifier()


def test_mastodon_notifier_missing_access_token(monkeypatch):
    monkeypatch.delenv("MASTODON_ACCESS_TOKEN", raising=False)
    with pytest.raises(ValueError):
        mastodon_notifier()


def test_bsky_notifier_missing_credentials(monkeypatch):
    monkeypatch.delenv("BSKY_USERNAME", raising=False)
    monkeypatch.delenv("BSKY_PASSWORD", raising=False)
    with pytest.raises(ValueError):
        bsky_notifier()
