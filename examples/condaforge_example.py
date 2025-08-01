#!/usr/bin/env python3
"""Example showing how to use the CondaForgeProvider for monitoring conda-forge packages."""

from glasscandle.watcher import Watcher


def main():
    """Demonstrate CondaForgeProvider usage."""
    # Create a watcher
    watcher = Watcher("condaforge_versions.json")
    
    # Monitor packages from conda-forge
    print("=== CondaForge Provider Examples ===")
    
    # Example 1: Monitor any version of numpy from conda-forge
    watcher.condaforge("numpy")
    print("✓ Registered numpy from conda-forge (any version)")
    
    # Example 2: Monitor specific version range
    watcher.condaforge("scipy", version=">=1.7,<2.0")
    print("✓ Registered scipy from conda-forge (>=1.7,<2.0)")
    
    # Example 3: Monitor with callback
    def on_package_update(key, old_version, new_version):
        print(f"🔔 {key}: {old_version} → {new_version}")
    
    watcher.condaforge("matplotlib", version=">=3.5", on_change=on_package_update)
    print("✓ Registered matplotlib from conda-forge (>=3.5) with callback")
    
    # Example 4: Compatible release constraint
    watcher.condaforge("pandas", version="~=1.5.0")
    print("✓ Registered pandas from conda-forge (~=1.5.0)")
    
    print("\n=== Running Version Check ===")
    
    # Run the version check
    try:
        updated = watcher.run(warn=True)
        if updated:
            print("✅ Some packages had version updates!")
        else:
            print("ℹ️  No version updates found")
    except Exception as e:
        print(f"❌ Error during version check: {e}")
    

if __name__ == "__main__":
    main()
