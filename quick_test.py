#!/usr/bin/env python3
"""Quick test of QReviewer with Kiro backend."""

import os
import sys

# Set environment variables
os.environ["GITHUB_TOKEN"] = os.environ.get("GITHUB_TOKEN", "your_github_token_here")
os.environ["QREVIEWER_LLM_BACKEND"] = "amazon_q"
os.environ["Q_CLI_HOST"] = "192.168.1.100"
os.environ["Q_CLI_USER"] = "bryan"
os.environ["Q_CLI_PORT"] = "22"

print("🧪 Quick QReviewer Test with Amazon Q Backend")
print("=" * 45)

try:
    # Test imports
    print("📦 Testing imports...")
    from qrev.config import config
    from qrev.llm_client import get_llm_client
    print("✅ All imports successful")
    
    # Test configuration
    print("\n🔧 Configuration:")
    print(f"   Backend: {config.llm_backend}")
    print(f"   GitHub Token: {'Set' if config.github_token else 'Missing'}")
    print(f"   Q CLI Host: {config.q_cli_host}")
    print(f"   Q CLI User: {config.q_cli_user}")
    
    # Test LLM client
    print("\n🤖 LLM Client:")
    client = get_llm_client()
    print(f"   Client Type: {type(client).__name__}")
    
    # Test configuration validation
    print("\n✅ Validation:")
    is_valid = config.validate()
    print(f"   Configuration Valid: {is_valid}")
    
    if is_valid:
        print("\n🎉 QReviewer is properly configured with Kiro backend!")
        print("   You can now run: python -m qrev.cli review-only --pr <PR_URL>")
    else:
        print("\n⚠️  Configuration issues detected. Check the output above.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()