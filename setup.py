#!/usr/bin/env python3
"""
QReviewer Setup Script
Installs dependencies and validates the installation
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and handle errors gracefully."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def main():
    print("🚀 QReviewer Setup")
    print("=" * 50)
    
    # Install core dependencies
    core_deps = "typer rich requests pydantic"
    if not run_command(f"pip3 install {core_deps}", "Installing core dependencies"):
        print("❌ Failed to install core dependencies")
        return 1
    
    # Install optional dependencies (don't fail if these don't work)
    optional_deps = "fastapi uvicorn jinja2 httpx tenacity boto3 aiohttp"
    run_command(f"pip3 install {optional_deps}", "Installing optional dependencies")
    
    # Test the installation
    print("\n🧪 Testing installation...")
    try:
        import typer, rich, requests, pydantic
        print("✅ Core dependencies imported successfully")
    except ImportError as e:
        print(f"❌ Import test failed: {e}")
        return 1
    
    # Test QReviewer import
    try:
        sys.path.insert(0, os.getcwd())
        import qrev.config
        print("✅ QReviewer modules imported successfully")
    except ImportError as e:
        print(f"⚠️  QReviewer import test failed: {e}")
        print("   This might be normal if optional dependencies are missing")
    
    print("\n🎉 Setup complete!")
    print("\n📖 Next steps:")
    print("1. Set your GitHub token: export GITHUB_TOKEN='your_token_here'")
    print("2. Test QReviewer: python qreview.py --help")
    print("3. Run a review: python qreview.py https://github.com/owner/repo/pull/123")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())