#!/usr/bin/env python3
"""Example showing all providers including the new CondaForgeProvider."""

from glasscandle.watcher import Watcher


def main():
    """Demonstrate all provider types including CondaForgeProvider."""
    # Create a watcher
    watcher = Watcher("all_providers_versions.json")
    
    print("=== Multi-Provider Example ===")
    
    # Define a common callback
    def package_updated(key, old_version, new_version):
        provider_type = key.split("::")[0]
        package_name = key.split("::", 1)[1]
        print(f"🔔 {provider_type.upper()}: {package_name} {old_version} → {new_version}")
    
    # PyPI packages
    print("✓ Registering PyPI packages...")
    watcher.pypi("requests", version=">=2.25", on_change=package_updated)
    watcher.pypi("numpy", on_change=package_updated)
    
    # Conda packages (general, multiple channels)
    print("✓ Registering Conda packages...")
    watcher.conda("pytorch", channels=["pytorch", "conda-forge"], on_change=package_updated)
    
    # Conda-forge packages (new provider)
    print("✓ Registering Conda-forge packages...")
    watcher.condaforge("matplotlib", version=">=3.5", on_change=package_updated)
    watcher.condaforge("scipy", version=">=1.7,<2.0", on_change=package_updated)
    watcher.condaforge("pandas", on_change=package_updated)
    
    # Bioconda packages
    print("✓ Registering Bioconda packages...")
    watcher.bioconda("samtools", version=">=1.15", on_change=package_updated)
    watcher.bioconda("blast", on_change=package_updated)
    
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
    
    # Display summary by provider type
    print("\n=== Package Summary by Provider ===")
    for provider_type, packages in watcher.db.data.items():
        if isinstance(packages, dict):
            print(f"  {provider_type.upper()}:")
            for package_name, version in packages.items():
                print(f"    {package_name}: v{version}")
        else:
            # Handle legacy flat keys
            if "::" in provider_type:
                provider, package = provider_type.split("::", 1)
                print(f"  {provider.upper()}: {package} v{packages}")
            else:
                print(f"  UNKNOWN: {provider_type} v{packages}")


if __name__ == "__main__":
    main()
