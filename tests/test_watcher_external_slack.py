import pytest
import requests
from glasscandle.notifications.slack import send_slack_msg


@pytest.fixture
def webhook_url():
    return "https://example.com/slack/webhook"


def test_send_slack_msg_with_title_only(webhook_url, mocker):
    mocker.patch("os.getenv", return_value=webhook_url)
    mocker.patch("requests.post")

    title = "Test Title"
    send_slack_msg(title)

    requests.post.assert_called_once_with(
        webhook_url,
        json={
            "text": title,
            "blocks": [{"type": "section", "text": {"type": "mrkdwn", "text": title}}],
        },
    )


def test_send_slack_msg_with_title_and_content(webhook_url, mocker):
    mocker.patch("os.getenv", return_value=webhook_url)
    mocker.patch("requests.post")

    title = "Test Title"
    content = "Test Content"
    send_slack_msg(title, content)

    requests.post.assert_called_once_with(
        webhook_url,
        json={
            "text": title,
            "blocks": [
                {"type": "section", "text": {"type": "mrkdwn", "text": title}},
                {"type": "section", "text": {"type": "mrkdwn", "text": content}},
            ],
        },
    )


def test_send_slack_msg_with_title_content_and_url(webhook_url, mocker):
    mocker.patch("os.getenv", return_value=webhook_url)
    mocker.patch("requests.post")

    title = "Test Title"
    content = "Test Content"
    url = "https://example.com"
    send_slack_msg(title, content, url)

    requests.post.assert_called_once_with(
        webhook_url,
        json={
            "text": title,
            "blocks": [
                {"type": "section", "text": {"type": "mrkdwn", "text": title}},
                {"type": "section", "text": {"type": "mrkdwn", "text": content}},
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Click here for more details -> {url}",
                    },
                },
            ],
        },
    )


def test_send_slack_msg_missing_webhook_url():
    with pytest.raises(ValueError):
        send_slack_msg("Test Title")
