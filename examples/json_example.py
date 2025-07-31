"""Example showing the JSON provider functionality."""

from glasscandle import Watcher

def notify_version_change(key: str, old_version: str, new_version: str):
    """Custom callback function for version changes."""
    print("🔄 JSON VERSION CHANGE DETECTED!")
    print(f"   Key: {key}")
    print(f"   Old: {old_version}")
    print(f"   New: {new_version}")
    print("   ───────────────────────")

# Create watcher instance
watch = Watcher("json_example_versions.json")

# Monitor GitHub releases using JSON API
watch.json(
    "https://api.github.com/repos/microsoft/vscode/releases/latest",
    "$.tag_name",
    on_change=notify_version_change
)

# Monitor npm package registry
watch.json(
    "https://registry.npmjs.org/react/latest",
    "$.version",
    on_change=notify_version_change
)

# Monitor complex nested JSON structure
watch.json(
    "https://httpbin.org/json",
    "$.slideshow.slides[0].title",
    on_change=notify_version_change
)

if __name__ == "__main__":
    print("Running watcher with JSON providers...")
    watch.run()
