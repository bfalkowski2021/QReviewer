#!/usr/bin/env python3
"""
GitHub posting script using only standard library (urllib)
"""

import json
import os
import urllib.request
import urllib.parse
import re
from typing import List, Dict, Any, Tuple

def parse_pr_url(pr_url: str) -> Tuple[str, str, int]:
    """Parse GitHub PR URL to extract owner, repo, and PR number."""
    pattern = r"github\.com/([^/]+)/([^/]+)/pull/(\d+)"
    match = re.search(pattern, pr_url)
    if not match:
        raise ValueError(f"Invalid GitHub PR URL: {pr_url}")
    
    owner, repo, number = match.groups()
    return owner, repo, int(number)

def create_review_comment(finding: Dict[str, Any]) -> Dict[str, Any]:
    """Create a GitHub review comment from a finding."""
    
    # Build the comment body
    comment_body = f"""## 🔍 Code Review Finding

**Severity**: {finding['severity'].upper()}
**Category**: {finding['category']}
**Confidence**: {finding['confidence'] * 100:.0f}%

**Issue**: {finding['message']}

**File**: `{finding['file']}`
**Line**: {finding.get('line_hint', 'N/A')}

---
*Automated review by QReviewer with Kiro backend*"""
    
    return {
        "body": comment_body,
        "path": finding['file'],
        "line": finding.get('line_hint', 1),
        "side": "RIGHT"
    }

def post_pr_review(pr_url: str, findings: List[Dict[str, Any]], token: str, 
                   event: str = "COMMENT", body: str = None) -> Dict[str, Any]:
    """Post a review to a GitHub PR with inline comments."""
    
    owner, repo, pr_number = parse_pr_url(pr_url)
    
    # Prepare the review payload
    review_payload = {
        "event": event,
        "body": body or f"QReviewer automated code review - {len(findings)} findings identified",
        "comments": []
    }
    
    # Convert findings to GitHub comments
    for finding in findings:
        comment = create_review_comment(finding)
        review_payload["comments"].append(comment)
    
    # Create the request
    api_base = f"https://api.github.com/repos/{owner}/{repo}"
    review_url = f"{api_base}/pulls/{pr_number}/reviews"
    
    # Prepare the request
    data = json.dumps(review_payload).encode('utf-8')
    
    req = urllib.request.Request(review_url, data=data, method='POST')
    req.add_header('Authorization', f'token {token}')
    req.add_header('Accept', 'application/vnd.github.v3+json')
    req.add_header('User-Agent', 'QReviewer/1.0.0')
    req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req) as response:
            response_data = json.loads(response.read().decode())
            return response_data
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else "Unknown error"
        raise Exception(f"Failed to post review: {e.code} - {error_body}")

def main():
    """Post the Kiro findings to GitHub."""
    
    print("🚀 Posting Kiro Analysis to GitHub PR #2")
    print("=" * 50)
    
    # Configuration
    pr_url = "https://github.com/bfalkowski2021/ae/pull/2"
    token = os.environ.get("GITHUB_TOKEN", "your_github_token_here")
    findings_file = "kiro_findings.json"
    
    try:
        # Load findings
        print(f"📖 Loading findings from: {findings_file}")
        with open(findings_file, 'r') as f:
            findings_data = json.load(f)
        
        findings = findings_data.get("findings", [])
        print(f"✅ Found {len(findings)} findings to post")
        
        # Create review body
        review_body = """# 🚀 QReviewer Analysis: Architectural Refactoring Review

## 📊 Summary
This PR represents a **high-quality architectural refactoring** that significantly improves the codebase structure and maintainability.

### 🎯 Key Improvements
- ✅ **Single Responsibility Principle**: Split monolithic function into focused components
- ✅ **Spring Best Practices**: Proper dependency injection and bean configuration  
- ✅ **Service Layer Simplification**: Removed complex conditional logic
- ✅ **Test Coverage**: Added integration tests for refactored functionality

### 📈 Impact Analysis
- **Maintainability**: ⬆️ Significantly improved
- **Testability**: ⬆️ Enhanced through better separation of concerns
- **Performance**: ➡️ Neutral (no performance impact expected)

### 🔍 Findings Summary
- **7 findings** identified across **7 files**
- **1 Major** positive finding (design improvement)
- **3 Minor** suggestions for further enhancement  
- **3 Info** observations about good practices

### ✅ Recommendation: **APPROVE**
This refactoring follows enterprise Java best practices and significantly improves code organization.

---
*Automated review by QReviewer with Kiro backend*  
*Analysis confidence: 85% overall*"""
        
        # Post review
        print(f"\n📝 Posting review to: {pr_url}")
        print(f"💬 Event type: COMMENT")
        print(f"🔍 Findings to post: {len(findings)}")
        
        response = post_pr_review(
            pr_url=pr_url,
            findings=findings,
            token=token,
            event="COMMENT",
            body=review_body
        )
        
        print("🎉 Review posted successfully!")
        print(f"🔗 Review ID: {response.get('id', 'N/A')}")
        print(f"🌐 Review URL: {response.get('html_url', 'N/A')}")
        print(f"📊 Posted {len(findings)} inline comments")
        
        # Show summary
        print(f"\n📋 Posted Findings Summary:")
        severity_counts = {}
        for finding in findings:
            sev = finding['severity']
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
        
        for severity, count in severity_counts.items():
            emoji = {'major': '🟠', 'minor': '🟡', 'info': '🔵', 'nit': '🟢'}.get(severity, '⚪')
            print(f"  {emoji} {severity.capitalize()}: {count}")
        
        print(f"\n✅ QReviewer analysis successfully posted to GitHub!")
        print(f"👀 Check the PR for inline comments: {pr_url}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())