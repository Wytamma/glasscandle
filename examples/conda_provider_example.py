#!/usr/bin/env python3
"""
Conda Provider Example

This example demonstrates the flexible conda provider that can monitor
packages from any conda channel, including conda-forge, bioconda, and
custom channels.
"""

from glasscandle import Watcher


def conda_change_callback(key: str, old_version: str, new_version: str):
    """Callback for conda package changes."""
    print(f"🔄 Conda package updated: {key}")
    print(f"    {old_version} → {new_version}")


def main():
    """Demonstrate conda provider functionality."""
    
    # Initialize watcher with callback
    watch = Watcher("conda_demo.json", on_change=conda_change_callback)
    
    print("📦 Setting up conda package monitoring...")
    
    # Default channel monitoring (conda-forge, defaults)
    print("\n🔧 Monitoring from default channels:")
    watch.conda("numpy")
    watch.conda("scipy")
    watch.conda("matplotlib")
    print("  - NumPy, SciPy, Matplotlib from default channels")
    
    # Specific channel monitoring
    print("\n🤖 Monitoring from specific channels:")
    
    # PyTorch from pytorch channel
    watch.conda("pytorch", channels=["pytorch", "conda-forge"])
    print("  - PyTorch from pytorch and conda-forge channels")
    
    # TensorFlow from conda-forge
    watch.conda("tensorflow", channels=["conda-forge"])
    print("  - TensorFlow from conda-forge")
    
    # Bioinformatics tools from bioconda
    watch.conda("samtools", channels=["bioconda"])
    watch.conda("bwa", channels=["bioconda"])
    watch.conda("minimap2", channels=["bioconda"])
    print("  - Bioinformatics tools from bioconda")
    
    # Channel-prefixed package names (alternative syntax)
    print("\n🏷️ Monitoring with channel prefixes:")
    watch.conda("conda-forge::xarray")
    watch.conda("bioconda::blast")
    watch.conda("pytorch::torchvision")
    print("  - Using channel prefix syntax")
    
    # Version constraints with channels
    print("\n📏 Monitoring with version constraints:")
    watch.conda("pandas", version=">=1.5,<2.0", channels=["conda-forge"])
    watch.conda("scikit-learn", version="~=1.2.0", channels=["conda-forge"])
    print("  - Pandas 1.x and scikit-learn ~1.2.0 from conda-forge")
    
    # Mixed provider example
    print("\n🔀 Mixed provider monitoring:")
    
    # Same package from different sources for comparison
    watch.pypi("numpy")  # PyPI version
    watch.conda("numpy", channels=["conda-forge"])  # Conda version
    watch.bioconda("blast")  # Bioconda (legacy method)
    watch.conda("blast", channels=["bioconda"])  # Same via conda provider
    print("  - Comparing versions across PyPI, conda-forge, and bioconda")
    
    print("\n🔍 Running conda monitoring...")
    
    try:
        watch.run()
        print("✅ Conda monitoring completed successfully!")
        
        # Show monitored packages grouped by provider
        print("\n📊 Currently monitored packages:")
        
        for provider, packages in watch.db.data.items():
            if packages:  # Only show providers with packages
                print(f"\n  {provider.title()} packages:")
                for package, version in packages.items():
                    print(f"    - {package}: {version}")
                
    except Exception as e:
        print(f"❌ Error during conda monitoring: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
