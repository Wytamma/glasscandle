# GitHub Actions Setup

This guide shows you how to set up GitHub Actions to automatically run Watcher on a schedule or when code changes are pushed to your repository.

## Overview

GitHub Actions allows you to run Watcher automatically in the cloud, making it perfect for:
- Monitoring packages, APIs, or websites on a schedule
- Getting notifications when changes are detected
- Maintaining a persistent database of version history

## Basic Setup

### 1. Create the Workflow File

Create a file at `.github/workflows/watcher.yml` in your repository:

```yaml
name: GlassCandle
on:
  # push:
  #   branches: 
  #     - master
  #     - main
  schedule:
      - cron: '0 0 * * *' # Run daily at midnight
  workflow_dispatch: # Allow manual triggering


jobs:
  glasscandle:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: pip install glasscandle
      
      - name: Run GlassCandle
        env:
          # Slack webhook URL stored as GitHub secret
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
          # Email notifications (stored as secrets)
          EMAIL_TO: ${{ secrets.EMAIL_TO }}
          EMAIL_SMTP_SERVER: ${{ secrets.EMAIL_SMTP_SERVER }}
          EMAIL_USERNAME: ${{ secrets.EMAIL_USERNAME }}
          EMAIL_PASSWORD: ${{ secrets.EMAIL_PASSWORD }}
          # Mastodon (stored as secrets)
          MASTODON_ACCESS_TOKEN: ${{ secrets.MASTODON_ACCESS_TOKEN }}
          MASTODON_API_BASE_URL: ${{ secrets.MASTODON_API_BASE_URL }}
          # Bluesky (stored as secrets)
          BSKY_USERNAME: ${{ secrets.BSKY_USERNAME }}
          BSKY_PASSWORD: ${{ secrets.BSKY_PASSWORD }}

        run: python examples/watch.py # Example script to run GlassCandle

      - name: Commit and push version database changes
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GlassCandle"
          git add .
          git diff --staged --quiet || git commit -m "Update version database [skip ci]"
          git push

```

### 2. Create Your Watcher Script

Create a Python script (e.g., `watcher_script.py`) in your repository:

```python
from glasscandle import Watcher

# Initialize watcher with a database file
watcher = Watcher(db_path="versions.json")

# Add your watchers
watcher.pypi("requests", on_change=lambda k, o, n: print(f"requests updated: {o} -> {n}"))
watcher.url("https://api.github.com/repos/microsoft/vscode/releases/latest", 
           parser="$.tag_name", 
           on_change=lambda k, o, n: print(f"VS Code updated: {o} -> {n}"))

# Run the watcher
watcher.run()
```

## Adding Notifications

To get notified when changes are detected, you'll need to set up notification secrets and environment variables.

### Setting Up GitHub Secrets

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the secrets you need for your notification methods

### Slack Notifications

Add this secret:
- `SLACK_WEBHOOK_URL`: Your Slack webhook URL

Update your workflow to include the environment variable:

```yaml
- name: Run watcher with notifications
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
  run: python watcher_script.py
```

Update your watcher script:

```python
from glasscandle import Watcher
from glasscandle.notifications import slack_notifier
import os

# Create notification function
slack_notify = slack_notifier(
    webhook_url=os.getenv('SLACK_WEBHOOK_URL'),
    channel="#updates"
)

watcher = Watcher(db_path="versions.json")
watcher.pypi("requests", on_change=slack_notify)
watcher.run()
```

### Email Notifications

Add these secrets:
- `EMAIL_TO`: Recipient email address
- `EMAIL_SMTP_SERVER`: SMTP server (e.g., smtp.gmail.com)
- `EMAIL_USERNAME`: Your email username
- `EMAIL_PASSWORD`: Your email password or app password

Update your workflow:

```yaml
- name: Run watcher with email notifications
  env:
    EMAIL_TO: ${{ secrets.EMAIL_TO }}
    EMAIL_SMTP_SERVER: ${{ secrets.EMAIL_SMTP_SERVER }}
    EMAIL_USERNAME: ${{ secrets.EMAIL_USERNAME }}
    EMAIL_PASSWORD: ${{ secrets.EMAIL_PASSWORD }}
  run: python watcher_script.py
```

Update your watcher script:

```python
from glasscandle import Watcher
from glasscandle.notifications import email_notifier
import os

email_notify = email_notifier(
    to_email=os.getenv('EMAIL_TO'),
    smtp_server=os.getenv('EMAIL_SMTP_SERVER'),
    username=os.getenv('EMAIL_USERNAME'),
    password=os.getenv('EMAIL_PASSWORD')
)

watcher = Watcher(db_path="versions.json")
watcher.pypi("requests", on_change=email_notify)
watcher.run()
```

### Mastodon Notifications

Add these secrets:
- `MASTODON_ACCESS_TOKEN`: Your Mastodon access token
- `MASTODON_API_BASE_URL`: Your Mastodon instance URL (e.g., https://mastodon.social)

```python
from glasscandle.notifications import mastodon_notifier
import os

mastodon_notify = mastodon_notifier(
    access_token=os.getenv('MASTODON_ACCESS_TOKEN'),
    api_base_url=os.getenv('MASTODON_API_BASE_URL')
)
```

### BlueSky Notifications

Add these secrets:
- `BSKY_USERNAME`: Your BlueSky username
- `BSKY_PASSWORD`: Your BlueSky password

```python
from glasscandle.notifications import bsky_notifier
import os

bsky_notify = bsky_notifier(
    username=os.getenv('BSKY_USERNAME'),
    password=os.getenv('BSKY_PASSWORD')
)
```

## Complete Example

Here's a complete example that combines multiple notification methods:

**.github/workflows/watcher.yml:**
```yaml
name: Package Watcher
on:
  schedule:
    - cron: '0 */6 * * *' # Run every 6 hours
  workflow_dispatch: # Allow manual triggering

jobs:
  watch:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - run: pip install glasscandle
      
      - name: Run watcher
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
          EMAIL_TO: ${{ secrets.EMAIL_TO }}
          EMAIL_SMTP_SERVER: ${{ secrets.EMAIL_SMTP_SERVER }}
          EMAIL_USERNAME: ${{ secrets.EMAIL_USERNAME }}
          EMAIL_PASSWORD: ${{ secrets.EMAIL_PASSWORD }}
        run: python watch_packages.py

      - name: Commit database changes
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add versions.json || true
          git diff --staged --quiet || git commit -m "Update package versions [skip ci]"
          git push || true
```

**watch_packages.py:**
```python
from glasscandle import Watcher
from glasscandle.notifications import slack_notifier, email_notifier, multi_notifier
import os

# Set up notifications
notifications = []

if os.getenv('SLACK_WEBHOOK_URL'):
    slack_notify = slack_notifier(
        webhook_url=os.getenv('SLACK_WEBHOOK_URL'),
        channel="#package-updates"
    )
    notifications.append(slack_notify)

if os.getenv('EMAIL_TO'):
    email_notify = email_notifier(
        to_email=os.getenv('EMAIL_TO'),
        smtp_server=os.getenv('EMAIL_SMTP_SERVER'),
        username=os.getenv('EMAIL_USERNAME'),
        password=os.getenv('EMAIL_PASSWORD'),
        subject="Package Update Alert"
    )
    notifications.append(email_notify)

# Combine all notification methods
notify = multi_notifier(*notifications) if notifications else None

# Set up watcher
watcher = Watcher(db_path="versions.json")

# Watch various packages
packages_to_watch = [
    "requests",
    "numpy", 
    "pandas",
    "django",
    "flask"
]

for package in packages_to_watch:
    watcher.pypi(package, on_change=notify)

# Watch GitHub releases
watcher.url("https://api.github.com/repos/microsoft/vscode/releases/latest",
           parser="$.tag_name",
           key="vscode",
           on_change=notify)

# Run the watcher
print("Starting package watcher...")
watcher.run()
print("Watcher completed successfully!")
```

## Advanced Configuration

### Custom Schedules

You can customize when your watcher runs using cron syntax:

```yaml
schedule:
  - cron: '0 9 * * 1-5'  # Weekdays at 9 AM UTC
  - cron: '0 */4 * * *'  # Every 4 hours
  - cron: '0 0 1 * *'    # First day of every month
```

### Multiple Environments

You can set up different workflows for different environments:

```yaml
strategy:
  matrix:
    environment: [production, staging]
    
steps:
  - name: Run watcher
    env:
      ENVIRONMENT: ${{ matrix.environment }}
    run: python watcher_${{ matrix.environment }}.py
```

### Error Handling

Add error handling to your workflow:

```yaml
- name: Run watcher
  continue-on-error: true
  run: python watcher_script.py

- name: Notify on failure
  if: failure()
  run: |
    echo "Watcher failed, sending alert..."
    # Add failure notification logic here
```

## Troubleshooting

### Common Issues

1. **Permission denied when pushing**: Make sure your repository has Actions permission to write to the repository
2. **Secrets not accessible**: Verify secrets are set correctly in repository settings
3. **Python package conflicts**: Pin specific versions in requirements.txt
4. **Rate limiting**: Add delays between requests or reduce frequency

### Debugging

Add debug output to your watcher script:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Your watcher code here
```

Enable step debugging in your workflow:

```yaml
- name: Debug environment
  run: |
    echo "Python version: $(python --version)"
    echo "Working directory: $(pwd)"
    echo "Files: $(ls -la)"
    env
```

## Security Best Practices

1. **Use secrets**: Never hardcode sensitive information like API keys or passwords
2. **Limit permissions**: Use the principle of least privilege for your workflows
3. **Review dependencies**: Regularly update and audit your Python dependencies
4. **Monitor logs**: Regularly check your Action logs for any suspicious activity

This setup will automatically monitor your specified packages and URLs, sending notifications when changes are detected, all running in GitHub's cloud infrastructure.
