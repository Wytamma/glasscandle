import os
from typing import Callable, List, Optional, Union

# Import all external notification services
from .slack import send_slack_msg
from .email import send_email
from .mastodon import send_mastodon_post, toot  # noqa: F401
from .bsky import send_bsky_post

def _extract_url_from_key(key: str, include_url: bool = True) -> Optional[str]:
    """Extract URL from a watcher key if applicable.
    
    Args:
        key: The watcher key (e.g., "pypi::requests", "url::https://...", "bioconda::samtools")
        include_url: Whether to extract URLs at all
    
    Returns:
        URL string if extractable and include_url is True, otherwise None
    """
    if not include_url:
        return None
    
    if key.startswith("url::"):
        return key[5:]  # Remove "url::" prefix
    elif key.startswith("pypi::"):
        package = key[6:]
        return f"https://pypi.org/project/{package}/"
    elif key.startswith("bioconda::"):
        package = key[10:]
        return f"https://anaconda.org/bioconda/{package}"
    
    return None


def slack_notifier(include_url: bool = True) -> Callable[[str, str, str], None]:
    """Create a Slack notification callback for version changes.
    
    Args:
        include_url: Whether to include package/URL links in notifications
    
    Returns:
        Callback function suitable for use with on_change parameter
    
    Environment Variables:
        SLACK_WEBHOOK_URL: Slack webhook URL (used if webhook_url is None)
    """
    if not os.getenv("SLACK_WEBHOOK_URL"):
        raise ValueError("SLACK_WEBHOOK_URL environment variable is required for Slack notifications")

    def notify(key: str, old_version: str, new_version: str) -> None:
        """
    Enhanced notification helpers for watcher callbacks.
    """
        title = f"📦 Version Update: {key}"
        content = f"Updated from `{old_version}` → `{new_version}`"
        
        url = _extract_url_from_key(key, include_url)
        send_slack_msg(title, content, url)
    
    return notify


def email_notifier() -> Callable[[str, str, str], None]:
    """Create an email notification callback for version changes.
    
    Args:
        smtp_config: Dictionary with email configuration (if None, uses environment variables)
    
    Returns:
        Callback function suitable for use with on_change parameter
    
    Environment Variables (used if smtp_config is None):
        EMAIL_TO: Recipient email address
        EMAIL_FROM: Sender email address
        EMAIL_SMTP_SERVER: SMTP server hostname
        EMAIL_SMTP_PORT: SMTP server port (default: 587)
        EMAIL_USERNAME: SMTP username
        EMAIL_PASSWORD: SMTP password
    """
    # Get config from environment if not provided
    
    smtp_config = {
        "to": os.getenv("EMAIL_TO"),
        "from": os.getenv("EMAIL_FROM"),
        "smtp_server": os.getenv("EMAIL_SMTP_SERVER"),
        "smtp_port": int(os.getenv("EMAIL_SMTP_PORT", "587")),
        "username": os.getenv("EMAIL_USERNAME"),
        "password": os.getenv("EMAIL_PASSWORD"),
    }
    
    # Validate required fields
    required_fields = ["to", "smtp_server", "username", "password"]
    missing_fields = [field for field in required_fields if not smtp_config.get(field)]
    if missing_fields:
        raise ValueError(f"Missing required email configuration: {', '.join(missing_fields)}")
    
    def notify(key: str, old_version: str, new_version: str) -> None:
        """
    Enhanced notification helpers for watcher callbacks.
    """
        try:
            subject = f"Version Update: {key}"
            body = f"Package {key} has been updated from {old_version} to {new_version}"
            send_email(
                to=smtp_config["to"],
                subject=subject,
                body=body,
                smtp_config=smtp_config
            )
        except ImportError:
            print("[WARN] Email notifications not available - email module not found")
        except Exception as e:
            print(f"[WARN] Email notification failed: {e}")
    
    return notify


def mastodon_notifier(
    include_url: bool = True
) -> Callable[[str, str, str], None]:
    """Create a Mastodon notification callback for version changes.
    
    Args:
        include_url: Whether to include package/URL links in notifications
    
    Returns:
        Callback function suitable for use with on_change parameter
    
    Environment Variables:
        MASTODON_ACCESS_TOKEN: Mastodon access token (used if access_token is None)
        MASTODON_API_BASE_URL: Mastodon instance URL (used if api_base_url is None)
    """
    if not os.getenv("MASTODON_ACCESS_TOKEN"):
        raise ValueError("MASTODON_ACCESS_TOKEN environment variable is required for Mastodon notifications")

    def notify(key: str, old_version: str, new_version: str) -> None:
        """
    Enhanced notification helpers for watcher callbacks.
    """
        try:
            title = f"📦 Version Update: {key}"
            content = f"Updated from {old_version} → {new_version}"
            
            url = _extract_url_from_key(key, include_url)
            send_mastodon_post(title, content, url)
        except Exception as e:
            print(f"[WARN] Mastodon notification failed: {e}")
    
    return notify


def bsky_notifier(
    service_url: str = "https://bsky.social",
    include_url: bool = True
) -> Callable[[str, str, str], None]:
    """Create a Bluesky notification callback for version changes.
    
    Args:
        service_url: Bluesky service URL (default: https://bsky.social)
        include_url: Whether to include package/URL links in notifications
    
    Returns:
        Callback function suitable for use with on_change parameter
    
    Environment Variables:
        BSKY_USERNAME: Bluesky username (used if username is None)
        BSKY_PASSWORD: Bluesky password (used if password is None)
    """
    if not os.getenv("BSKY_USERNAME") or not os.getenv("BSKY_PASSWORD"):
        raise ValueError("BSKY_USERNAME and BSKY_PASSWORD environment variables are required for Bluesky notifications")
    
    def notify(key: str, old_version: str, new_version: str) -> None:
        """
    Enhanced notification helpers for watcher callbacks.
    """
        try:
            title = f"📦 Version Update: {key}"
            content = f"Updated from {old_version} → {new_version}"
            
            url = _extract_url_from_key(key, include_url)
            send_bsky_post(title, content, url, service_url=service_url)
        except Exception as e:
            print(f"[WARN] Bluesky notification failed: {e}")
    
    return notify


def _call_notifiers(notifiers: Union[Callable[[str, str, str], None], List[Callable[[str, str, str], None]]], 
                   key: str, old_version: str, new_version: str) -> None:
    """Call one or more notification callbacks.
    
    Args:
        notifiers: Either a single callback function or a list of callback functions
        key: The watcher key (e.g., "pypi::requests")
        old_version: Previous version
        new_version: New version
    """
    if callable(notifiers):
        # Single notifier
        try:
            notifiers(key, old_version, new_version)
        except Exception as e:
            print(f"[WARN] Notification failed: {e}")
    elif isinstance(notifiers, (list, tuple)):
        # Multiple notifiers
        for notifier in notifiers:
            try:
                notifier(key, old_version, new_version)
            except Exception as e:
                print(f"[WARN] Notification failed: {e}")
    else:
        raise TypeError(f"notifiers must be callable or list/tuple of callables, got {type(notifiers)}")


# Legacy function for backward compatibility
def multi_notifier(*notifiers: Callable[[str, str, str], None]) -> Callable[[str, str, str], None]:
    """Combine multiple notification methods into a single callback.
    
    Args:
        *notifiers: Variable number of notification callback functions
    
    Returns:
        Combined callback that calls all provided notifiers
        
    Note:
        This function is deprecated. Use a list instead: [notifier1, notifier2, ...]
    """
    def notify(key: str, old_version: str, new_version: str) -> None:
        """
    Enhanced notification helpers for watcher callbacks.
    """
        _call_notifiers(list(notifiers), key, old_version, new_version)
    
    return notify
