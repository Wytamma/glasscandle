# Notification Methods

This document describes the various notification methods available in the watcher package for alerting about version changes.

## Quick Start

The easiest way to set up notifications is using the built-in notification helpers:

```python
from glasscandle import Watcher
from glasscandle.notifications import slack_notifier, multi_notifier

# Set up notifications using environment variables
slack_notify = slack_notifier()  # Uses SLACK_WEBHOOK_URL env var

watch = Watcher("my_config.json")
watch.pypi("requests", on_change=slack_notify)
watch.run()
```

## Available Notification Methods

### 1. Slack Notifications

Send notifications to Slack via webhooks.

**Environment Variables:**
- `SLACK_WEBHOOK_URL` - Your Slack webhook URL

**Usage:**
```python
from glasscandle.notifications import slack_notifier

# Using environment variable
slack_notify = slack_notifier()

# Or specify webhook URL directly
slack_notify = slack_notifier(webhook_url="https://hooks.slack.com/...")

# Use with watcher
watch.pypi("django", on_change=slack_notify)
```

### 2. Email Notifications

Send notifications via SMTP email.

**Environment Variables:**
- `EMAIL_TO` - Recipient email address
- `EMAIL_FROM` - Sender email address (optional, defaults to username)
- `EMAIL_SMTP_SERVER` - SMTP server hostname
- `EMAIL_SMTP_PORT` - SMTP server port (default: 587)
- `EMAIL_USERNAME` - SMTP username
- `EMAIL_PASSWORD` - SMTP password

**Usage:**
```python
from glasscandle.notifications import email_notifier

# Using environment variables
email_notify = email_notifier()

# Or specify config directly
email_notify = email_notifier(smtp_config={
    "to": "admin@example.com",
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "username": "your_email@gmail.com",
    "password": "your_app_password"
})

watch.pypi("fastapi", on_change=email_notify)
```

### 3. Mastodon Notifications

Post notifications to Mastodon instances.

**Environment Variables:**
- `MASTODON_ACCESS_TOKEN` - Your Mastodon access token
- `MASTODON_API_BASE_URL` - Your Mastodon instance URL

**Installation:**
```bash
pip install Mastodon.py
```

**Usage:**
```python
from glasscandle.notifications import mastodon_notifier

# Using environment variables
mastodon_notify = mastodon_notifier()

# Or specify credentials directly
mastodon_notify = mastodon_notifier(
    access_token="your_token",
    api_base_url="https://mastodon.social"
)

watch.pypi("pandas", on_change=mastodon_notify)
```

### 4. Bluesky Notifications

Post notifications to Bluesky via AT Protocol.

**Environment Variables:**
- `BSKY_USERNAME` - Your Bluesky username/handle
- `BSKY_PASSWORD` - Your Bluesky password or app password

**Usage:**
```python
from glasscandle.notifications import bsky_notifier

# Using environment variables
bsky_notify = bsky_notifier()

# Or specify credentials directly
bsky_notify = bsky_notifier(
    username="your_handle.bsky.social",
    password="your_password"
)

watch.pypi("numpy", on_change=bsky_notify)
```

## Combining Multiple Notifications

Use `multi_notifier` to send notifications through multiple channels:

```python
from glasscandle.notifications import (
    slack_notifier, email_notifier, mastodon_notifier, 
    bsky_notifier, multi_notifier
)

# Set up individual notifiers
slack_notify = slack_notifier()
email_notify = email_notifier()
mastodon_notify = mastodon_notifier()

# Combine them
combined_notify = multi_notifier(
    slack_notify,
    email_notify,
    mastodon_notify
)

watch.pypi("requests", on_change=combined_notify)
```

## Custom Notifications

You can create custom notification functions:

```python
def custom_notify(key: str, old_version: str, new_version: str):
    """Custom notification logic."""
    print(f"🔄 {key}: {old_version} → {new_version}")
    
    # Add your custom logic here
    # - Send to Discord
    # - Update a dashboard
    # - Write to a log file
    # - etc.

watch.pypi("django", on_change=custom_notify)
```

## Error Handling

All notification methods include error handling. If a notification fails, it will log a warning but won't stop the watcher:

```python
# This will continue working even if some notifications fail
combined_notify = multi_notifier(
    slack_notify,      # Might fail if webhook is invalid
    email_notify,      # Might fail if SMTP config is wrong
    mastodon_notify    # Might fail if token is expired
)
```

## Security Best Practices

1. **Use Environment Variables:** Store sensitive credentials in environment variables, not in code
2. **App Passwords:** Use app-specific passwords for email services (Gmail, Outlook, etc.)
3. **Token Rotation:** Regularly rotate API tokens and access keys
4. **Webhook Security:** Keep webhook URLs secret and regenerate if compromised

## Complete Example

```python
#!/usr/bin/env python3
"""Complete notification example with error handling."""

import os
from glasscandle import Watcher
from glasscandle.notifications import (
    slack_notifier, email_notifier, mastodon_notifier, 
    bsky_notifier, multi_notifier
)

def main():
    # Set up available notifiers
    notifiers = []
    
    try:
        slack_notify = slack_notifier()
        notifiers.append(slack_notify)
        print("✅ Slack notifications enabled")
    except ValueError:
        print("❌ Slack disabled (set SLACK_WEBHOOK_URL)")
    
    try:
        email_notify = email_notifier()
        notifiers.append(email_notify)
        print("✅ Email notifications enabled")
    except ValueError:
        print("❌ Email disabled (set EMAIL_* variables)")
    
    # Add more notifiers as needed...
    
    if not notifiers:
        print("⚠️  No notifications configured")
        return
    
    # Combine all available notifiers
    combined_notify = multi_notifier(*notifiers)
    
    # Set up watcher
    watch = Watcher("packages.json")
    watch.pypi("requests", on_change=combined_notify)
    watch.pypi("django", on_change=combined_notify)
    
    print(f"🚀 Starting watcher with {len(notifiers)} notification method(s)")
    watch.run()

if __name__ == "__main__":
    main()
```

See `examples/notifications_example.py` for more detailed examples.
