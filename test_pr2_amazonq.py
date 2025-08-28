#!/usr/bin/env python3
"""Test script for PR #2 with Amazon Q backend."""

import os
import sys
import json
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Set environment variables for testing
os.environ["GITHUB_TOKEN"] = os.environ.get("GITHUB_TOKEN", "your_github_token_here")
os.environ["QREVIEWER_LLM_BACKEND"] = "amazon_q"
os.environ["Q_CLI_HOST"] = "192.168.1.100"
os.environ["Q_CLI_USER"] = "bryan"
os.environ["Q_CLI_PORT"] = "22"
os.environ["QREVIEWER_VERBOSE"] = "true"

def test_github_fetch():
    """Test fetching PR data from GitHub."""
    print("🐙 Testing GitHub PR Fetch...")
    
    try:
        from qrev.github_api import fetch_pr_files
        
        pr_url = "https://github.com/bfalkowski2021/ae/pull/2"
        print(f"   Fetching: {pr_url}")
        
        pr_diff = fetch_pr_files(pr_url)
        
        if pr_diff and pr_diff.files:
            print(f"✅ Successfully fetched PR #{pr_diff.pr.number}")
            print(f"   Repository: {pr_diff.pr.repo}")
            print(f"   Files: {len(pr_diff.files)}")
            
            # Show files
            for file_info in pr_diff.files:
                print(f"   📄 {file_info.filename} ({file_info.status})")
            
            # Save raw data
            with open("pr2-raw-data.json", "w") as f:
                json.dump(pr_diff.dict(), f, indent=2)
            print(f"   💾 Raw data saved to pr2-raw-data.json")
            
            return pr_diff
        else:
            print("❌ Failed to fetch PR data")
            return None
            
    except Exception as e:
        print(f"❌ GitHub fetch failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_hunk_extraction(pr_diff):
    """Test extracting hunks from PR files."""
    print("\n📝 Testing Hunk Extraction...")
    
    try:
        from qrev.diff import extract_hunks_from_files
        
        hunks = extract_hunks_from_files(pr_diff.files)
        print(f"✅ Extracted {len(hunks)} hunks")
        
        # Show first few hunks
        for i, hunk in enumerate(hunks[:3]):
            print(f"   🔍 Hunk {i+1}: {hunk.file_path} ({hunk.hunk_header})")
            print(f"      Lines: {len(hunk.lines)}")
        
        if len(hunks) > 3:
            print(f"   ... and {len(hunks) - 3} more hunks")
        
        return hunks
        
    except Exception as e:
        print(f"❌ Hunk extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return []

def test_amazon_q_config():
    """Test Amazon Q configuration."""
    print("\n🔧 Testing Amazon Q Configuration...")
    
    try:
        from qrev.config import config
        from qrev.llm_client import get_llm_client
        
        print(f"✅ Configuration loaded")
        print(f"   Backend: {config.llm_backend}")
        print(f"   Q CLI Host: {config.q_cli_host}")
        print(f"   Q CLI User: {config.q_cli_user}")
        print(f"   Q CLI Port: {config.q_cli_port}")
        
        # Test client creation
        client = get_llm_client()
        print(f"✅ LLM client created: {type(client).__name__}")
        
        return True
        
    except Exception as e:
        print(f"❌ Amazon Q config test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_single_hunk_review(hunks):
    """Test reviewing a single hunk."""
    print("\n🤖 Testing Single Hunk Review...")
    
    if not hunks:
        print("❌ No hunks available for testing")
        return False
    
    try:
        from qrev.llm_client import review_hunk
        
        # Pick the first hunk
        test_hunk = hunks[0]
        print(f"   Testing hunk: {test_hunk.file_path} ({test_hunk.hunk_header})")
        print(f"   Lines in hunk: {len(test_hunk.lines)}")
        
        # Show hunk content
        print("   Hunk content:")
        for line in test_hunk.lines[:5]:  # Show first 5 lines
            print(f"     {line}")
        if len(test_hunk.lines) > 5:
            print(f"     ... and {len(test_hunk.lines) - 5} more lines")
        
        # Try to review it
        print("   🚀 Sending to Amazon Q for review...")
        findings = review_hunk(test_hunk, None)
        
        print(f"✅ Review completed: {len(findings)} findings")
        for finding in findings:
            print(f"   📋 {finding.severity.upper()}: {finding.message}")
        
        return True
        
    except Exception as e:
        print(f"❌ Hunk review failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the test."""
    print("🧪 QReviewer Test: PR #2 with Amazon Q Backend")
    print("=" * 55)
    
    # Test 1: Configuration
    if not test_amazon_q_config():
        print("❌ Configuration test failed, stopping")
        return 1
    
    # Test 2: GitHub fetch
    pr_diff = test_github_fetch()
    if not pr_diff:
        print("❌ GitHub fetch failed, stopping")
        return 1
    
    # Test 3: Hunk extraction
    hunks = test_hunk_extraction(pr_diff)
    if not hunks:
        print("❌ No hunks extracted, stopping")
        return 1
    
    # Test 4: Single hunk review
    if not test_single_hunk_review(hunks):
        print("❌ Hunk review failed")
        return 1
    
    print("\n🎉 All tests passed! QReviewer is working with Amazon Q backend.")
    print(f"📁 You can now review the full PR with:")
    print(f"   python -m qrev review-only --pr https://github.com/bfalkowski2021/ae/pull/2")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())