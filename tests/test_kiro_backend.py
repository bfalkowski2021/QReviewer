#!/usr/bin/env python3
"""
Test script for Kiro backend integration.
This script tests the Kiro backend without requiring a real PR.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the QReviewer package to the path
sys.path.insert(0, str(Path(__file__).parent))

from qrev.models import Hunk
from qrev.llm_client import KiroClient
from qrev.config import config

def test_kiro_config():
    """Test Kiro configuration."""
    print("🔧 Testing Kiro Configuration")
    print("=" * 40)
    
    # Set Kiro backend
    os.environ["QREVIEWER_LLM_BACKEND"] = "kiro"
    
    # Reload config
    from qrev.config import QReviewerConfig
    test_config = QReviewerConfig()
    
    print(f"Backend: {test_config.llm_backend}")
    print(f"API URL: {test_config.kiro_api_url}")
    print(f"Model: {test_config.kiro_model}")
    print(f"API Key: {'✅ Set' if test_config.kiro_api_key else '❌ Not set'}")
    print(f"Workspace: {test_config.kiro_workspace or '❌ Not set'}")
    print(f"Enabled: {test_config.llm_config.get('enabled', False)}")
    
    return test_config.validate()

async def test_kiro_client():
    """Test Kiro client with a sample hunk."""
    print("\n🚀 Testing Kiro Client")
    print("=" * 40)
    
    # Create a sample hunk for testing
    sample_hunk = Hunk(
        file_path="test.py",
        hunk_header="@@ -1,3 +1,4 @@",
        start_line=1,
        end_line=4,
        old_content="def hello():\n    print('Hello')\n    return True",
        new_content="def hello():\n    print('Hello World')\n    # TODO: Add error handling\n    return True"
    )
    
    try:
        # Create Kiro client
        client = KiroClient()
        print(f"✅ Kiro client created")
        print(f"   API URL: {client.kiro_config['api_url']}")
        print(f"   Model: {client.kiro_config['model']}")
        
        # Test review
        print(f"\n🔍 Testing review of sample hunk...")
        findings = await client.review_hunk(sample_hunk, "Focus on code quality and best practices.")
        
        print(f"✅ Review completed!")
        print(f"   Found {len(findings)} findings")
        
        for i, finding in enumerate(findings, 1):
            print(f"   {i}. [{finding.severity.upper()}] {finding.message}")
        
        return True
        
    except Exception as e:
        print(f"❌ Kiro client test failed: {e}")
        return False

def test_cli_integration():
    """Test CLI integration with backend flag."""
    print("\n🖥️  Testing CLI Integration")
    print("=" * 40)
    
    # Test that the backend flag is recognized
    try:
        from qrev.cli import app
        print("✅ CLI app imported successfully")
        
        # Test help to see if backend flag is there
        import subprocess
        result = subprocess.run([sys.executable, "-m", "qrev.cli", "review-only", "--help"], 
                              capture_output=True, text=True, cwd=Path(__file__).parent)
        
        if "--backend" in result.stdout:
            print("✅ Backend flag found in CLI help")
            return True
        else:
            print("❌ Backend flag not found in CLI help")
            return False
            
    except Exception as e:
        print(f"❌ CLI integration test failed: {e}")
        return False

async def main():
    """Run all tests."""
    print("🧪 QReviewer Kiro Backend Test Suite")
    print("=" * 50)
    
    # Test 1: Configuration
    config_ok = test_kiro_config()
    
    # Test 2: CLI Integration
    cli_ok = test_cli_integration()
    
    # Test 3: Client (only if config is OK)
    client_ok = False
    if config_ok:
        client_ok = await test_kiro_client()
    else:
        print("\n⚠️  Skipping client test due to configuration issues")
    
    # Summary
    print("\n📊 Test Results")
    print("=" * 20)
    print(f"Configuration: {'✅ PASS' if config_ok else '❌ FAIL'}")
    print(f"CLI Integration: {'✅ PASS' if cli_ok else '❌ FAIL'}")
    print(f"Client Test: {'✅ PASS' if client_ok else '❌ FAIL' if config_ok else '⚠️  SKIPPED'}")
    
    if config_ok and cli_ok:
        print("\n🎉 Kiro backend integration is ready!")
        print("\nTo use Kiro backend:")
        print("  export QREVIEWER_LLM_BACKEND=kiro")
        print("  qrev review-only --backend kiro --pr <PR_URL>")
    else:
        print("\n⚠️  Some tests failed. Check configuration and dependencies.")
    
    return config_ok and cli_ok

if __name__ == "__main__":
    asyncio.run(main())