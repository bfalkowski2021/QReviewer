#!/usr/bin/env python3
"""Simple test to check if we can fetch the PR."""

import os
import sys
import json
from pathlib import Path

# Add the qrev module to the path
sys.path.insert(0, str(Path(__file__).parent))

# Set environment variables
os.environ['GITHUB_TOKEN'] = os.environ.get('GITHUB_TOKEN', 'your_github_token_here')

def main():
    try:
        print("Testing GitHub API connection...")
        
        from qrev.github_api import fetch_pr_files
        
        pr_url = "https://github.com/bfalkowski2021/ae/pull/2"
        
        print(f"🔍 Fetching PR: {pr_url}")
        
        # Fetch PR diff
        pr_diff = fetch_pr_files(pr_url)
        
        if not pr_diff:
            print("❌ Failed to fetch PR")
            return 1
        
        print(f"✅ Successfully fetched PR #{pr_diff.pr.number}")
        print(f"📁 Repository: {pr_diff.pr.repo}")
        print(f"🔗 URL: {pr_diff.pr.url}")
        print(f"📝 Found {len(pr_diff.files)} files")
        
        # Save the PR data
        output_file = "ae-pr2-data.json"
        with open(output_file, 'w') as f:
            json.dump(pr_diff.dict(), f, indent=2)
        
        print(f"📁 PR data saved to: {output_file}")
        
        # Show file list
        print("\n📋 Files in PR:")
        for file_info in pr_diff.files:
            print(f"  📄 {file_info.filename} ({file_info.status})")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())