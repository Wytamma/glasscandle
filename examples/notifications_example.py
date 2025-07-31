"""Example showing different notification integration approaches using environment variables."""

import os
from glasscandle import Watcher
from glasscandle.notifications import slack_notifier, email_notifier, mastodon_notifier, bsky_notifier, multi_notifier
from glasscandle.notifications.slack import send_slack_msg

# Approach 1: Using notification helpers with environment variables
def main_with_helpers():
    """Example using the notification helper functions with env vars."""
    watch = Watcher("notifications_example.json")
    
    # Create notification callbacks - credentials come from environment
    try:
        slack_notify = slack_notifier()  # Uses SLACK_WEBHOOK_URL env var
        
        # You can also create other notifiers using env vars
        # email_notify = email_notifier()  # Uses EMAIL_* env vars
        # mastodon_notify = mastodon_notifier()  # Uses MASTODON_* env vars
        # bsky_notify = bsky_notifier()  # Uses BSKY_* env vars
        
        # Combine multiple notification methods
        combined_notify = multi_notifier(
            slack_notify,
            # email_notify,  # Uncomment when email is set up
            # mastodon_notify,  # Uncomment when Mastodon is set up
            # bsky_notify,  # Uncomment when Bluesky is set up
        )
        
        # Register packages with notifications
        watch.pypi("requests", on_change=combined_notify)
        watch.bioconda("samtools", on_change=slack_notify)
        watch.json(
            "https://api.github.com/repos/microsoft/vscode/releases/latest",
            "$.tag_name",
            on_change=slack_notify
        )
        
        watch.run()
        
    except ValueError as e:
        print(f"[ERROR] Notification setup failed: {e}")
        print("Please set the required environment variables (see README for details)")


# Approach 2: Custom callback with direct external calls using env vars
def main_with_custom_callback():
    """Example using custom callbacks that call external functions directly."""
    
    # Get webhook URL from environment
    slack_webhook = os.getenv("SLACK_WEBHOOK_URL")
    if not slack_webhook:
        print("[ERROR] SLACK_WEBHOOK_URL environment variable not set")
        return
    
    def custom_notifier(key: str, old: str, new: str):
        """Custom notification logic using environment variables."""
        print(f"🔄 {key}: {old} → {new}")
        
        # Send to Slack using env var
        send_slack_msg(
            f"📦 Version Update: {key}",
            f"Updated from `{old}` → `{new}`"
        )
        
        # Send email using env vars (if email module exists)
        try:
            from glasscandle.notifications.email import send_email
            email_to = os.getenv("EMAIL_TO")
            if email_to:
                send_email(
                    to=email_to,
                    subject=f"Version Update: {key}",
                    body=f"Package {key} updated from {old} to {new}",
                    smtp_config={
                        "smtp_server": os.getenv("EMAIL_SMTP_SERVER"),
                        "username": os.getenv("EMAIL_USERNAME"),
                        "password": os.getenv("EMAIL_PASSWORD"),
                    }
                )
        except ImportError:
            pass  # Email not available
        
        # Could add more notification methods here using env vars:
        # - Discord webhook: DISCORD_WEBHOOK_URL
        # - Teams notification: TEAMS_WEBHOOK_URL
        # - Push notification: PUSHOVER_TOKEN, PUSHOVER_USER
        # - etc.
    
    watch = Watcher("notifications_example.json")
    watch.pypi("django", on_change=custom_notifier)
    watch.run()


# Approach 3: Provider-specific notifications using env vars
def main_with_provider_specific():
    """Example with different notifications for different providers using env vars."""
    
    # Get webhook URL from environment
    slack_webhook = os.getenv("SLACK_WEBHOOK_URL")
    if not slack_webhook:
        print("[ERROR] SLACK_WEBHOOK_URL environment variable not set")
        return
    
    # Different notification styles for different provider types
    def pypi_notifier(key: str, old: str, new: str):
        package = key.replace("pypi::", "")
        send_slack_msg(
            slack_webhook,
            f"🐍 PyPI Update: {package}",
            f"New version `{new}` available (was `{old}`)",
            f"https://pypi.org/project/{package}/"
        )
    
    def github_notifier(key: str, old: str, new: str):
        url = key.replace("url::", "")
        repo_name = url.split("/")[-3] + "/" + url.split("/")[-4]
        send_slack_msg(
            slack_webhook,
            f"🚀 GitHub Release: {repo_name}",
            f"New release `{new}` (was `{old}`)",
            url
        )
    
    watch = Watcher("notifications_example.json")
    
    # Different notifications for different types
    watch.pypi("fastapi", on_change=pypi_notifier)
    watch.json(
        "https://api.github.com/repos/tiangolo/fastapi/releases/latest",
        "$.tag_name",
        on_change=github_notifier
    )
    
    watch.run()


# Approach 4: Using all notification methods with environment variables
def main_with_all_notifiers():
    """Example using all available notification methods with env vars."""
    watch = Watcher("notifications_example.json")
    
    available_notifiers = []
    
    # Try to set up each notifier
    try:
        slack_notify = slack_notifier()
        available_notifiers.append(("Slack", slack_notify))
        print("✅ Slack notifications enabled")
    except ValueError:
        print("❌ Slack notifications disabled (missing SLACK_WEBHOOK_URL)")
    
    try:
        email_notify = email_notifier()
        available_notifiers.append(("Email", email_notify))
        print("✅ Email notifications enabled")
    except ValueError:
        print("❌ Email notifications disabled (missing email configuration)")
    
    try:
        mastodon_notify = mastodon_notifier()
        available_notifiers.append(("Mastodon", mastodon_notify))
        print("✅ Mastodon notifications enabled")
    except ValueError:
        print("❌ Mastodon notifications disabled (missing MASTODON_* env vars)")
    
    try:
        bsky_notify = bsky_notifier()
        available_notifiers.append(("Bluesky", bsky_notify))
        print("✅ Bluesky notifications enabled")
    except ValueError:
        print("❌ Bluesky notifications disabled (missing BSKY_* env vars)")
    
    if not available_notifiers:
        print("❌ No notification methods configured. Please set environment variables.")
        return
    
    # Create multi-notifier with all available methods
    all_notifiers = [notifier for _, notifier in available_notifiers]
    combined_notify = multi_notifier(*all_notifiers)
    
    print(f"\n🔔 Using {len(available_notifiers)} notification method(s): {', '.join([name for name, _ in available_notifiers])}")
    
    # Register packages with combined notifications
    watch.pypi("requests", on_change=combined_notify)
    watch.bioconda("samtools", on_change=combined_notify)
    watch.json(
        "https://api.github.com/repos/microsoft/vscode/releases/latest",
        "$.tag_name",
        on_change=combined_notify
    )
    
    print("🚀 Starting watcher with multi-platform notifications...")
    watch.run()


if __name__ == "__main__":
    print("Choose an approach:")
    print("1. Using notification helpers with env vars (recommended)")
    print("2. Custom callbacks with direct calls using env vars")
    print("3. Provider-specific notifications using env vars")
    print("4. Using all notification methods with env vars")
    print()
    print("Required environment variables:")
    print("  SLACK_WEBHOOK_URL - Slack webhook URL")
    print("  EMAIL_TO - Email recipient (optional)")
    print("  EMAIL_SMTP_SERVER - SMTP server (optional)")
    print("  EMAIL_USERNAME - SMTP username (optional)")
    print("  EMAIL_PASSWORD - SMTP password (optional)")
    print("  MASTODON_ACCESS_TOKEN - Mastodon access token (optional)")
    print("  MASTODON_API_BASE_URL - Mastodon instance URL (optional)")
    print("  BSKY_USERNAME - Bluesky username (optional)")
    print("  BSKY_PASSWORD - Bluesky password (optional)")
    print()
    
    choice = input("Enter choice (1-4): ")
    
    if choice == "1":
        main_with_helpers()
    elif choice == "2":
        main_with_custom_callback()
    elif choice == "3":
        main_with_provider_specific()
    elif choice == "4":
        main_with_all_notifiers()
    else:
        print("Invalid choice, running approach 1")
        main_with_helpers()
