"""Mastodon notification functionality."""

import os
from typing import Optional


def send_mastodon_post(
    title: str, 
    content: Optional[str] = None, 
    url: Optional[str] = None,
    access_token: Optional[str] = None,
    api_base_url: Optional[str] = None
) -> None:
    """Send a post to Mastodon.
    
    Args:
        title: Title/main content of the post
        content: Additional content (optional)
        url: URL to include in the post (optional)
        access_token: Mastodon access token (if None, uses MASTODON_ACCESS_TOKEN env var)
        api_base_url: Mastodon instance URL (if None, uses MASTODON_API_BASE_URL env var)
    """
    try:
        from mastodon import Mastodon
    except ImportError:
        print("[ERROR] Mastodon library not installed. Install with: pip install Mastodon.py")
        raise
    
    # Get credentials from environment if not provided
    if access_token is None:
        access_token = os.getenv("MASTODON_ACCESS_TOKEN")
        if not access_token:
            raise ValueError("Mastodon access token must be provided or set in MASTODON_ACCESS_TOKEN environment variable")
    
    if api_base_url is None:
        api_base_url = os.getenv("MASTODON_API_BASE_URL")
        if not api_base_url:
            raise ValueError("Mastodon API base URL must be provided or set in MASTODON_API_BASE_URL environment variable")
    
    # Build the post text
    post_text = title
    if content:
        post_text += f"\n\n{content}"
    if url:
        post_text += f"\n\n🔗 {url}"
    
    # Mastodon has a 500 character limit
    if len(post_text) > 500:
        post_text = post_text[:497] + "..."
    
    try:
        mastodon = Mastodon(
            access_token=access_token,
            api_base_url=api_base_url
        )
        mastodon.toot(post_text)
    except Exception as e:
        print(f"[ERROR] Failed to send Mastodon post: {e}")
        raise


# Keep the legacy function for backward compatibility
def toot(access_token: str, api_base_url: str, text: str) -> None:
    """Legacy function for sending a toot."""
    try:
        from mastodon import Mastodon
        mastodon = Mastodon(
            access_token=access_token,
            api_base_url=api_base_url
        )
        mastodon.toot(text[:499])
    except Exception as e:
        print(f"[ERROR] Failed to send toot: {e}")
        raise
