"""Bluesky (AT Protocol) notification functionality."""

import os
import requests
from datetime import datetime, timezone
from typing import Optional


def send_bsky_post(
    title: str,
    content: Optional[str] = None,
    url: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    service_url: str = "https://bsky.social"
) -> None:
    """Send a post to Bluesky via AT Protocol.
    
    Args:
        title: Title/main content of the post
        content: Additional content (optional)
        url: URL to include in the post (optional)
        username: Bluesky username/handle (if None, uses BSKY_USERNAME env var)
        password: Bluesky password/app password (if None, uses BSKY_PASSWORD env var)
        service_url: Bluesky service URL (default: https://bsky.social)
    """
    # Get credentials from environment if not provided
    if username is None:
        username = os.getenv("BSKY_USERNAME")
        if not username:
            raise ValueError("Bluesky username must be provided or set in BSKY_USERNAME environment variable")
    
    if password is None:
        password = os.getenv("BSKY_PASSWORD")
        if not password:
            raise ValueError("Bluesky password must be provided or set in BSKY_PASSWORD environment variable")
    
    # Build the post text
    post_text = title
    if content:
        post_text += f"\n\n{content}"
    if url:
        post_text += f"\n\n🔗 {url}"
    
    # Bluesky has a 300 character limit
    if len(post_text) > 300:
        post_text = post_text[:297] + "..."
    
    try:
        # Create session
        session_response = requests.post(
            f"{service_url}/xrpc/com.atproto.server.createSession",
            json={
                "identifier": username,
                "password": password
            }
        )
        session_response.raise_for_status()
        session_data = session_response.json()
        
        access_jwt = session_data["accessJwt"]
        did = session_data["did"]
        
        # Create post
        post_response = requests.post(
            f"{service_url}/xrpc/com.atproto.repo.createRecord",
            headers={
                "Authorization": f"Bearer {access_jwt}",
                "Content-Type": "application/json"
            },
            json={
                "repo": did,
                "collection": "app.bsky.feed.post",
                "record": {
                    "text": post_text,
                    "createdAt": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        post_response.raise_for_status()
        
    except requests.RequestException as e:
        print(f"[ERROR] Failed to send Bluesky post: {e}")
        raise
    except Exception as e:
        print(f"[ERROR] Unexpected error sending Bluesky post: {e}")
        raise
