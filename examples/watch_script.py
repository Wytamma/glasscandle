#!/usr/bin/env python3
"""
Version watcher script for GitH    # Python packages - all use default callback
    watch.pypi("requests")
    watch.pypi("fastapi", version=">=0.100,<1.0")  # Only update within 0.x series
    watch.pypi("django", version=">=4.0,<5.0")     # Only update within 4.x series
    watch.pypi("flask")
    
    # Bioconda packages - all use default callback (legacy method)
    watch.bioconda("samtools", version=">=1.15,<2.0")  # Avoid major version 2
    watch.bioconda("bwa")
    watch.bioconda("blast")
    
    # Conda packages with new provider - all use default callback  
    watch.conda("bowtie2")  # searches default channels: conda-forge, bioconda
    watch.conda("minimap2", channels=["bioconda"])  # searches only bioconda
    watch.conda("bioconda::seqtk", version="~=1.3")  # explicit channel, compatible releaseis script is designed to run in CI/CD environments and uses environment
variables for all sensitive configuration.

Required environment variables:
- SLACK_WEBHOOK_URL: Slack webhook URL for notifications

Optional environment variables:
- EMAIL_TO: Email recipient for notifications
- EMAIL_SMTP_SERVER: SMTP server hostname
- EMAIL_USERNAME: SMTP username
- EMAIL_PASSWORD: SMTP password
- DISCORD_WEBHOOK_URL: Discord webhook URL
- TEAMS_WEBHOOK_URL: Microsoft Teams webhook URL
"""

import os
import sys
from glasscandle import Watcher
from glasscandle.notifications import slack_notifier, email_notifier, multi_notifier


def main():
    """Main watcher script for GitHub Actions."""
    
    # Initialize watcher with persistent database
    watch = Watcher("versions.json")
    
    # Set up notifications
    notifications = []
    
    # Slack notifications (required)
    try:
        slack_notify = slack_notifier()
        notifications.append(slack_notify)
        print("✅ Slack notifications enabled")
    except ValueError as e:
        print(f"[ERROR] Slack setup failed: {e}")
    
    # Email notifications (optional)
    email_to = os.getenv("EMAIL_TO")
    if email_to:
        try:
            email_notify = email_notifier()
            notifications.append(email_notify)
            print("✅ Email notifications enabled")
        except ValueError as e:
            print(f"[WARN] Email setup failed: {e}")
    
    # Initialize watcher with default notification callback
    watch = Watcher("versions.json", on_change=notifications)
    
    # Register packages to monitor (all will use default notifications)
    print("📦 Registering packages to monitor...")
    
    # Python packages - all use default callback
    watch.pypi("requests")
    watch.pypi("fastapi", version=">=0.100,<1.0")  # Only update within 0.x series
    watch.pypi("django", version=">=4.0,<5.0")     # Only update within 4.x series
    watch.pypi("flask")
    
    # Bioconda packages - all use default callback (legacy method)
    watch.bioconda("samtools", version=">=1.15,<2.0")  # Avoid major version 2
    watch.bioconda("bwa")
    watch.bioconda("blast")
    
    # Conda packages with new provider - all use default callback  
    watch.conda("bowtie2")  # searches default channels: conda-forge, bioconda
    watch.conda("minimap2", channels=["bioconda"])  # searches only bioconda
    watch.conda("bioconda::seqtk", version="~=1.3")  # explicit channel, compatible release
    
    # GitHub releases (JSON API) - all use default callback
    watch.json(
        "https://api.github.com/repos/microsoft/vscode/releases/latest",
        "$.tag_name"
    )
    
    # Custom URL monitoring - uses default callback
    @watch.response("https://api.github.com/repos/actions/runner/releases/latest")
    def github_runner_version(res):
        """Monitor GitHub Actions runner releases."""
        return res.json()["tag_name"]
    
    # Run the version checks
    print("🔍 Checking for version updates...")
    try:
        watch.run()
        print("✅ Version check completed successfully")
    except Exception as e:
        print(f"[ERROR] Version check failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
