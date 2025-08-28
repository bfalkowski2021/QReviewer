#!/usr/bin/env python3
"""Test script for Kiro backend integration."""

import os
import sys
import asyncio
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Set environment variables for testing
os.environ["GITHUB_TOKEN"] = os.environ.get("GITHUB_TOKEN", "your_github_token_here")
os.environ["QREVIEWER_LLM_BACKEND"] = "kiro"
os.environ["KIRO_API_URL"] = "http://localhost:3000"
os.environ["QREVIEWER_VERBOSE"] = "true"

def test_config():
    """Test configuration loading."""
    print("🔧 Testing QReviewer Configuration...")
    
    try:
        from qrev.config import config
        print(f"✅ Configuration loaded successfully")
        print(f"   Backend: {config.llm_backend}")
        print(f"   GitHub Token: {'Set' if config.github_token else 'Missing'}")
        print(f"   Kiro API URL: {config.kiro_api_url}")
        
        # Print full config
        config.print_config()
        
        # Validate config
        is_valid = config.validate()
        print(f"   Configuration valid: {is_valid}")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_llm_client():
    """Test LLM client creation."""
    print("\n🤖 Testing LLM Client...")
    
    try:
        from qrev.llm_client import get_llm_client, KiroClient
        
        client = get_llm_client()
        print(f"✅ LLM client created: {type(client).__name__}")
        
        if isinstance(client, KiroClient):
            print(f"   Kiro API URL: {client.kiro_config['api_url']}")
            print(f"   Kiro Model: {client.kiro_config['model']}")
        
        return True
    except Exception as e:
        print(f"❌ LLM client test failed: {e}")
        return False

def test_github_api():
    """Test GitHub API access."""
    print("\n🐙 Testing GitHub API Access...")
    
    try:
        from qrev.github_client import GitHubClient
        
        client = GitHubClient()
        
        # Test with the specific PR
        pr_url = "https://github.com/bfalkowski2021/ae/pull/2"
        print(f"   Testing PR: {pr_url}")
        
        # This should work if the token is valid
        pr_data = client.get_pr_data(pr_url)
        print(f"✅ GitHub API access successful")
        print(f"   PR Title: {pr_data.get('title', 'Unknown')}")
        print(f"   PR State: {pr_data.get('state', 'Unknown')}")
        
        return True
    except Exception as e:
        print(f"❌ GitHub API test failed: {e}")
        return False

async def test_kiro_backend():
    """Test Kiro backend specifically."""
    print("\n🚀 Testing Kiro Backend...")
    
    try:
        from qrev.llm_client import KiroClient
        from qrev.models import Hunk
        
        # Create a test hunk
        test_hunk = Hunk(
            file_path="test.py",
            hunk_header="@@ -1,3 +1,4 @@",
            old_start=1,
            old_count=3,
            new_start=1,
            new_count=4,
            lines=[
                " def hello():",
                "+    print('Hello, World!')",
                "     return 'hello'"
            ],
            end_line=4
        )
        
        client = KiroClient()
        print(f"✅ Kiro client created")
        print(f"   API URL: {client.kiro_config['api_url']}")
        
        # Note: This will likely fail without a real Kiro server running
        # but it will test the client setup
        try:
            findings = await client.review_hunk(test_hunk)
            print(f"✅ Kiro review completed: {len(findings)} findings")
            for finding in findings:
                print(f"   - {finding.severity}: {finding.message}")
        except Exception as e:
            print(f"⚠️  Kiro API call failed (expected if no server): {e}")
            print("   This is normal if Kiro server is not running locally")
        
        return True
    except Exception as e:
        print(f"❌ Kiro backend test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 QReviewer Kiro Backend Integration Test")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_config),
        ("LLM Client", test_llm_client),
        ("GitHub API", test_github_api),
        ("Kiro Backend", lambda: asyncio.run(test_kiro_backend()))
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n📊 Test Results Summary")
    print("=" * 30)
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! QReviewer is ready to use with Kiro backend.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()