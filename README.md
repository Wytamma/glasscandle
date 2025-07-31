
![](https://raw.githubusercontent.com/Wytamma/glasscandle/refs/heads/main/docs/images/logo.png)

A flexible, modular version monitoring tool that tracks changes across multiple sources including PyPI, Bioconda, and custom URLs.

[![PyPI - Version](https://img.shields.io/pypi/v/glasscandle.svg)](https://pypi.org/project/glasscandle)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/glasscandle.svg)](https://pypi.org/project/glasscandle)
[![write-the - docs](https://badgen.net/badge/write-the/docs/blue?icon=https://raw.githubusercontent.com/Wytamma/write-the/master/images/write-the-icon.svg)](https://write-the.wytamma.com/)
[![write-the - test](https://badgen.net/badge/write-the/tests/green?icon=https://raw.githubusercontent.com/Wytamma/write-the/master/images/write-the-icon.svg)](https://github.com/Wytamma/glasscandle/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/Wytamma/glasscandle/graph/badge.svg?token=J6tzIs9inI)](https://codecov.io/gh/Wytamma/glasscandle)


-----

**Table of Contents**

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Supported Providers](#supported-providers)
- [Usage Examples](#usage-examples)
- [License](#license)

## Features

- 🔍 **Multi-source monitoring** - Track versions from PyPI, Bioconda, and arbitrary URLs
- 🎯 **Flexible parsing** - Built-in parsers for common formats (ETag, regex, JSON)
- 🔧 **Custom parsers** - Write your own parsers for specialized sources
- 💾 **Persistent storage** - JSON-based database to track version changes
- 📢 **Change notifications** - Execute custom callbacks when versions change
- 🌐 **HTTP resilience** - Built-in retries and error handling
- 🏗️ **Modular architecture** - Clean separation of concerns for easy extension

## Installation

```console
pip install glasscandle
```

## Quick Start

```python
from glasscandle import Watcher

# Create a watcher instance
watch = Watcher("versions.json")

# Optional: Add change notification callback
def on_version_change(key: str, old: str, new: str):
    print(f"📦 {key} updated: {old} → {new}")

# Monitor PyPI packages
watch.pypi("requests", on_change=on_version_change)
watch.pypi("numpy")

# Monitor Bioconda packages
watch.bioconda("samtools", on_change=on_version_change)
watch.bioconda("bwa")

# Monitor a URL with ETag parsing (default)
watch.url("https://example.com/releases/latest")

# Monitor a URL with regex parsing
watch.url_regex(
    "https://example.com/version", 
    r"version:\s*(\d+\.\d+\.\d+)",
    on_change=on_version_change
)

# Run checks once
watch.run()

# Or run continuously (every 60 seconds)
watch.start(interval=60)
```

## Supported Providers

### PyPI
Monitor Python packages from the Python Package Index:
```python
watch.pypi("package-name")
```

### Bioconda
Monitor bioinformatics packages from Bioconda:
```python
watch.bioconda("package-name")
```

### JSON APIs
Monitor JSON endpoints using JSONPath expressions:
```python
# GitHub releases
watch.json("https://api.github.com/repos/user/repo/releases/latest", "$.tag_name")

# npm packages
watch.json("https://registry.npmjs.org/package/latest", "$.version")

# Complex nested paths
watch.json("https://api.example.com/data", "$.results[0].version")
```

### URL with Built-in Parsers
Monitor arbitrary URLs using built-in parsers:
```python
# ETag parser (default)
watch.url("https://example.com/file")

# Last-Modified parser
from glasscandle import last_modified
watch.url("https://example.com/file", parser=last_modified)

# SHA256 hash parser
from glasscandle import sha256_of_body
watch.url("https://example.com/file", parser=sha256_of_body)

# Regex parser
watch.url_regex("https://example.com/version", r"v(\d+\.\d+\.\d+)")

# JSON parser with JSONPath
watch.json("https://api.github.com/repos/user/repo/releases/latest", "$.tag_name")
```

### Custom URL Parsers
Write custom parsers for specialized sources:
```python
from glasscandle import Response

@watch.response("https://api.github.com/repos/user/repo/releases/latest")
def github_latest_release(res: Response):
    """Extract the latest release tag from GitHub API."""
    data = res.json()
    return data["tag_name"]
```

### Change Notifications
Execute custom functions when versions change:
```python
def notify_change(key: str, old_version: str, new_version: str):
    print(f"📦 {key} updated: {old_version} → {new_version}")
    # Send email, webhook, Slack notification, etc.

# Add callbacks to any provider
watch.pypi("requests", on_change=notify_change)
watch.bioconda("samtools", on_change=notify_change)
watch.json("https://api.github.com/repos/user/repo/releases/latest", "$.tag_name", on_change=notify_change)
watch.url("https://example.com/version", on_change=notify_change)

# Custom URLs with callbacks
@watch.response("https://api.github.com/repos/user/repo/releases", 
                on_change=notify_change)
def custom_parser(res: Response):
    return res.json()[0]["tag_name"]
```

### Built-in Notification Helpers
Use pre-built notification functions for common services:
```python
from glasscandle.notifications import slack_notifier, multi_notifier

# Slack notifications (uses SLACK_WEBHOOK_URL env var)
slack_notify = slack_notifier()
watch.pypi("django", on_change=slack_notify)

# Email notifications (uses EMAIL_* env vars)  
email_notify = email_notifier()
watch.bioconda("samtools", on_change=email_notify)

# Multiple notification methods
multi_notify = multi_notifier(slack_notify, email_notify)
watch.json("https://api.github.com/repos/user/repo/releases/latest", 
           "$.tag_name", on_change=multi_notify)

# Direct external function calls
from glasscandle.external.slack import send_slack_msg
import os

def custom_notifier(key: str, old: str, new: str):
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    send_slack_msg(f"Version Update: {key}", f"Updated from {old} → {new}", webhook_url=webhook_url)

watch.pypi("requests", on_change=custom_notifier)
```

## GitHub Actions Integration

Watcher is designed to work seamlessly with GitHub Actions for automated monitoring:

### 1. Environment Variables
Set these as GitHub repository secrets:
- `SLACK_WEBHOOK_URL` - Required for Slack notifications
- `EMAIL_TO` - Optional email recipient
- `EMAIL_SMTP_SERVER` - Optional SMTP server
- `EMAIL_USERNAME` - Optional SMTP username  
- `EMAIL_PASSWORD` - Optional SMTP password

### 2. GitHub Actions Workflow
Create `.github/workflows/version-watcher.yml`:
```yaml
name: Version Watcher
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

jobs:
  watch-versions:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - run: pip install watcher
    - run: python watch_script.py
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
    - run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add .
        git diff --staged --quiet || git commit -m "Update versions [skip ci]"
        git push
```

### 3. Watch Script
Create a `watch_script.py` that uses environment variables:
```python
import os
from glasscandle import Watcher
from glasscandle.notifications import slack_notifier

watch = Watcher("versions.json")
notify = slack_notifier()  # Uses SLACK_WEBHOOK_URL env var

watch.pypi("requests", on_change=notify)
watch.json("https://api.github.com/repos/user/repo/releases/latest", 
           "$.tag_name", on_change=notify)

watch.run()
```

## Usage Examples

### Basic Version Monitoring
```python
from glasscandle import Watcher

watch = Watcher("my-versions.json")

# Add packages to monitor
watch.pypi("django")
watch.pypi("flask")
watch.bioconda("blast")

# Check once
watch.run()
```

### Advanced URL Monitoring
```python
from glasscandle import Watcher, regex, etag

watch = Watcher("versions.json")

# Monitor with different parsers
watch.url("https://releases.example.com/latest", parser=etag)
watch.url_regex("https://version.example.com", r"Version (\d+\.\d+)")
watch.json("https://api.example.com/version", "$.latest")

# Custom domain restrictions
watch = Watcher(
    "versions.json", 
    allowed_custom_domains=("trusted.com", "example.org")
)
```

### Continuous Monitoring
```python
from glasscandle import Watcher

watch = Watcher("versions.json")

# Add your packages
watch.pypi("requests")
watch.bioconda("samtools")
watch.json("https://api.github.com/repos/user/repo/releases/latest", "$.tag_name")

# Start monitoring (checks every 5 minutes)
watch.start(interval=300)
```


## License

`watcher` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
