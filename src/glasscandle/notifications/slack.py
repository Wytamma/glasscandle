import requests
import os

def send_slack_msg(title: str, content: str = None, url: str = None, webhook_url = None) -> None:
    """Send a message to a Slack channel via webhook.
    Args:
        hook_url: Slack webhook URL
        title: Title of the message
        content: Optional Content of the message
        url: Optional URL to include in the message
    """
    if not webhook_url:
        webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        raise ValueError("Slack webhook URL must be provided or set in SLACK_WEBHOOK_URL environment variable")

    data = {
        "text": title,
        "blocks": [
            {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": title
                    }
                },
        ]
    }
    if content:
        data["blocks"].append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": content
            }
        })
    if url:
        data["blocks"].append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"Click here for more details -> {url}"
            }
        })
    try:
        r = requests.post(webhook_url, json=data)
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"[ERROR] Failed to send Slack message: {e}")
        raise
        