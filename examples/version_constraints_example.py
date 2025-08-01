#!/usr/bin/env python3
"""
Version Constraints Example

This example demonstrates how to use version constraints to monitor only
specific version ranges of packages, preventing unwanted major version
updates or monitoring only compatible releases.
"""

from glasscandle import Watcher


def version_change_callback(key: str, old_version: str, new_version: str):
    """Custom callback to handle version changes."""
    print(f"🔄 {key}: {old_version} → {new_version}")


def main():
    """Demonstrate version constraint usage."""
    
    # Initialize watcher
    watch = Watcher("version_constraints_demo.json", on_change=version_change_callback)
    
    print("📦 Setting up version constraint monitoring...")
    
    # PyPI Examples
    print("\n🐍 PyPI packages with version constraints:")
    
    # Monitor only Django 4.x versions (avoid Django 5.x)
    watch.pypi("django", version=">=4.0,<5.0")
    print("  - Django: Only 4.x versions (>=4.0,<5.0)")
    
    # Monitor compatible releases (patch-level updates only)
    watch.pypi("requests", version="~=2.28.0")
    print("  - Requests: Compatible with 2.28.x (~=2.28.0)")
    
    # Complex constraint with exclusions
    watch.pypi("flask", version=">=2.0,!=2.1.0,<3.0")
    print("  - Flask: 2.x but not 2.1.0 (>=2.0,!=2.1.0,<3.0)")
    
    # Monitor latest stable (no pre-releases)
    watch.pypi("fastapi", version=">=0.100")
    print("  - FastAPI: Stable versions only (>=0.100)")
    
    # Conda Examples
    print("\n🐍 Conda packages with version constraints:")
    
    # Monitor NumPy from conda-forge, only 1.x versions
    watch.conda("numpy", version=">=1.21,<2.0", channels=["conda-forge"])
    print("  - NumPy: 1.x versions from conda-forge (>=1.21,<2.0)")
    
    # Monitor PyTorch from specific channel with compatible release
    watch.conda("pytorch", version="~=1.12.0", channels=["pytorch"])
    print("  - PyTorch: Compatible with 1.12.x (~=1.12.0)")
    
    # Bioconda Examples  
    print("\n🧬 Bioconda packages with version constraints:")
    
    # Monitor BLAST, avoiding version 2.13.x which had issues
    watch.bioconda("blast", version=">=2.12,!=2.13.0,<2.14")
    print("  - BLAST: 2.12+ but not 2.13.0 (>=2.12,!=2.13.0,<2.14)")
    
    # Monitor SAMtools compatible releases
    watch.bioconda("samtools", version="~=1.15.0")
    print("  - SAMtools: Compatible with 1.15.x (~=1.15.0)")
    
    # Example without constraints (monitors all versions)
    watch.bioconda("bwa")
    print("  - BWA: All versions (no constraints)")
    
    print("\n🔍 Running version checks...")
    
    # Perform the version checks
    try:
        watch.run()
        print("✅ Version constraint monitoring completed successfully!")
        
        # Show current state
        print("\n📊 Current monitored versions:")
        for provider, packages in watch.db.data.items():
            print(f"  {provider}:")
            for package, version in packages.items():
                print(f"    - {package}: {version}")
            
    except Exception as e:
        print(f"❌ Error during monitoring: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
