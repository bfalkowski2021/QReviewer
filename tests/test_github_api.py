#!/usr/bin/env python3
"""Test GitHub API directly without dependencies."""

import json
import urllib.request
import urllib.parse
import os

def fetch_pr_info(pr_url, token):
    """Fetch PR information from GitHub API."""
    # Parse PR URL to extract owner, repo, and PR number
    # Expected format: https://github.com/owner/repo/pull/number
    parts = pr_url.rstrip('/').split('/')
    if len(parts) < 7 or parts[2] != 'github.com':
        raise ValueError(f"Invalid PR URL format: {pr_url}")
    
    owner = parts[3]
    repo = parts[4]
    pr_number = parts[6]
    
    # GitHub API URL
    api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    
    # Create request with authentication
    req = urllib.request.Request(api_url)
    req.add_header('Authorization', f'token {token}')
    req.add_header('Accept', 'application/vnd.github.v3+json')
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return data
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}")
        if e.code == 401:
            print("Authentication failed. Check your GitHub token.")
        elif e.code == 404:
            print("PR not found. Check the URL.")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def fetch_pr_files(pr_url, token):
    """Fetch PR files from GitHub API."""
    # Parse PR URL
    parts = pr_url.rstrip('/').split('/')
    owner = parts[3]
    repo = parts[4]
    pr_number = parts[6]
    
    # GitHub API URL for PR files
    api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
    
    # Create request
    req = urllib.request.Request(api_url)
    req.add_header('Authorization', f'token {token}')
    req.add_header('Accept', 'application/vnd.github.v3+json')
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return data
    except Exception as e:
        print(f"Error fetching files: {e}")
        return None

def main():
    # Configuration
    pr_url = "https://github.com/bfalkowski2021/ae/pull/2"
    token = os.environ.get("GITHUB_TOKEN", "your_github_token_here")
    
    print("🧪 Testing GitHub API Access")
    print("=" * 40)
    print(f"PR URL: {pr_url}")
    print(f"Token: {token[:20]}...")
    print()
    
    # Test PR info
    print("📋 Fetching PR information...")
    pr_info = fetch_pr_info(pr_url, token)
    
    if pr_info:
        print(f"✅ PR #{pr_info['number']}: {pr_info['title']}")
        print(f"📁 Repository: {pr_info['base']['repo']['full_name']}")
        print(f"👤 Author: {pr_info['user']['login']}")
        print(f"🔄 State: {pr_info['state']}")
        print(f"📊 Additions: +{pr_info['additions']}, Deletions: -{pr_info['deletions']}")
        print()
        
        # Test PR files
        print("📄 Fetching PR files...")
        files = fetch_pr_files(pr_url, token)
        
        if files:
            print(f"✅ Found {len(files)} files:")
            for file_info in files:
                status = file_info['status']
                filename = file_info['filename']
                additions = file_info['additions']
                deletions = file_info['deletions']
                print(f"  📄 {filename} ({status}) +{additions}/-{deletions}")
            
            # Save results
            result = {
                "pr_info": pr_info,
                "files": files
            }
            
            with open("ae-pr2-raw-data.json", "w") as f:
                json.dump(result, f, indent=2)
            
            print(f"\n📁 Raw data saved to: ae-pr2-raw-data.json")
            print("✅ GitHub API test successful!")
            
        else:
            print("❌ Failed to fetch PR files")
            return 1
    else:
        print("❌ Failed to fetch PR information")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())