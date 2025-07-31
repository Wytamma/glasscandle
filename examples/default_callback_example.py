"""Example showing default on_change callback usage."""

from glasscandle import Watcher
from glasscandle.notifications import slack_notifier

def default_notifier(key: str, old: str, new: str):
    """Default notification function for all version changes."""
    print(f"🔄 DEFAULT NOTIFICATION: {key}")
    print(f"   Changed from {old} to {new}")
    print("   ────────────────────────")

def special_notifier(key: str, old: str, new: str):
    """Special notification for important packages."""
    print(f"⚡ SPECIAL NOTIFICATION: {key}")
    print(f"   IMPORTANT UPDATE: {old} → {new}")
    print("   ════════════════════════")

def main():
    """Example showing default callback usage."""
    
    # Option 1: Set default callback in constructor
    watch = Watcher("default_callback_example.json", on_change=default_notifier)
    
    # These will use the default callback
    watch.pypi("requests")  # No on_change specified, uses default
    watch.bioconda("samtools")  # No on_change specified, uses default
    
    # This will use a specific callback (overrides default)
    watch.pypi("django", on_change=special_notifier)
    
    # JSON monitoring with default callback
    watch.json("https://api.github.com/repos/microsoft/vscode/releases/latest", "$.tag_name")
    
    # Custom response with specific callback
    @watch.response("https://api.github.com/repos/python/cpython/releases/latest", 
                    on_change=special_notifier)
    def python_version(res):
        return res.json()["tag_name"]
    
    print("Running watcher with default callbacks...")
    watch.run()

def main_with_slack_default():
    """Example using Slack as the default notification method."""
    
    # Set up Slack as default notification for all packages
    try:
        slack_notify = slack_notifier()  # Uses SLACK_WEBHOOK_URL env var
        
        watch = Watcher("slack_default_example.json", on_change=slack_notify)
        
        # All of these will send Slack notifications automatically
        watch.pypi("fastapi")
        watch.pypi("uvicorn") 
        watch.bioconda("blast")
        watch.json("https://api.github.com/repos/tiangolo/fastapi/releases/latest", "$.tag_name")
        
        # Only this one gets special handling
        def critical_notifier(key: str, old: str, new: str):
            # Send to both Slack (via default) and print urgently
            slack_notify(key, old, new)  # Explicitly call default too
            print(f"🚨 CRITICAL UPDATE: {key} - PLEASE REVIEW IMMEDIATELY!")
        
        watch.pypi("security-critical-package", on_change=critical_notifier)
        
        watch.run()
        
    except ValueError as e:
        print(f"[ERROR] Slack setup failed: {e}")
        print("Please set SLACK_WEBHOOK_URL environment variable")

def main_mixed_notifications():
    """Example showing mixed notification strategies."""
    
    def console_notifier(key: str, old: str, new: str):
        """Simple console notification as default."""
        print(f"📦 {key}: {old} → {new}")
    
    # Console notifications as default
    watch = Watcher("mixed_example.json", on_change=console_notifier)
    
    # Most packages use simple console notifications
    watch.pypi("numpy")
    watch.pypi("pandas")
    watch.pypi("matplotlib")
    
    # Important packages get Slack notifications
    try:
        slack_notify = slack_notifier()
        watch.pypi("django", on_change=slack_notify)
        watch.pypi("flask", on_change=slack_notify)
    except ValueError:
        print("[WARN] Slack not configured, using default notifications")
    
    # Custom behavior for specific package
    def custom_handler(key: str, old: str, new: str):
        print(f"🎯 CUSTOM: {key} updated to {new}")
        # Could trigger custom logic here:
        # - Update documentation
        # - Restart services
        # - Run tests
        # - etc.
    
    watch.pypi("my-custom-package", on_change=custom_handler)
    
    watch.run()

if __name__ == "__main__":
    print("Choose an example:")
    print("1. Basic default callback")
    print("2. Slack as default notification") 
    print("3. Mixed notification strategies")
    
    choice = input("Enter choice (1-3): ")
    
    if choice == "1":
        main()
    elif choice == "2":
        main_with_slack_default()
    elif choice == "3":
        main_mixed_notifications()
    else:
        print("Invalid choice, running basic example")
        main()
