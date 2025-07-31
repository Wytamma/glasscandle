"""Example showing the on_change callback functionality."""

from glasscandle import Watcher, Response

def notify_version_change(key: str, old_version: str, new_version: str):
    """Custom callback function for version changes."""
    print("🔄 VERSION CHANGE DETECTED!")
    print(f"   Key: {key}")
    print(f"   Old: {old_version}")
    print(f"   New: {new_version}")
    print("   ───────────────────────")

# Create watcher instance
watch = Watcher("example_versions.json")

# Register providers with on_change callbacks
watch.pypi("requests", on_change=notify_version_change)
watch.bioconda("samtools", on_change=notify_version_change)

# Register URL with callback
watch.url_regex(
    "https://httpbin.org/uuid",  # This will change each time
    r'"uuid":\s*"([^"]+)"',
    on_change=notify_version_change
)

# Register custom URL with decorator and callback
@watch.response("https://httpbin.org/uuid", on_change=notify_version_change)
def uuid_parser(res: Response):
    """Extract UUID from httpbin response."""
    data = res.json()
    return data["uuid"]

if __name__ == "__main__":
    print("Running watcher with on_change callbacks...")
    watch.run()
