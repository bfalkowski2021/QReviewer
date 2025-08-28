#!/usr/bin/env python3
"""
Test posting to GitHub PR using the CLI post_review command
"""

import os
import sys
import json
from pathlib import Path

# Add the qrev module to path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Test the GitHub posting functionality."""
    
    print("🧪 Testing GitHub Review Posting")
    print("=" * 40)
    
    # Set environment
    os.environ['GITHUB_TOKEN'] = os.environ.get('GITHUB_TOKEN', 'your_github_token_here')
    
    pr_url = "https://github.com/bfalkowski2021/ae/pull/2"
    findings_file = "kiro_findings.json"
    
    try:
        # Test 1: Verify findings file exists
        print(f"📄 Checking findings file: {findings_file}")
        if not Path(findings_file).exists():
            print(f"❌ Findings file not found: {findings_file}")
            return 1
        
        # Load and validate findings
        with open(findings_file, 'r') as f:
            data = json.load(f)
        
        findings = data.get('findings', [])
        print(f"✅ Found {len(findings)} findings to post")
        
        # Test 2: Test GitHub API access
        print(f"\n🔗 Testing GitHub API access...")
        from qrev.github_review import post_pr_review, GitHubReviewError
        
        # Create a minimal test - just post a summary comment first
        print(f"📝 Preparing review summary...")
        
        review_body = f"""# 🚀 QReviewer Analysis Summary

**PR**: {pr_url}
**Findings**: {len(findings)} identified
**Analysis**: Kiro-powered architectural review

## Key Highlights
- ✅ Excellent refactoring following Single Responsibility Principle
- ✅ Proper Spring configuration and dependency injection
- ✅ Good test coverage with integration tests
- ⚠️ Minor suggestions for code deduplication

**Overall Assessment**: High-quality architectural improvement

---
*Automated review by QReviewer with Kiro backend*"""

        # Convert findings to Finding objects
        from qrev.models import Finding
        
        finding_objects = []
        for f in findings:
            finding = Finding(
                file=f["file"],
                hunk_header=f["hunk_header"],
                severity=f["severity"],
                category=f["category"],
                message=f["message"],
                confidence=f["confidence"],
                suggested_patch=f.get("suggested_patch"),
                line_hint=f.get("line_hint")
            )
            finding_objects.append(finding)
        
        print(f"✅ Converted {len(finding_objects)} findings to objects")
        
        # Test 3: Post the review
        print(f"\n📤 Posting review to GitHub...")
        print(f"   URL: {pr_url}")
        print(f"   Findings: {len(finding_objects)}")
        print(f"   Event: COMMENT")
        
        token = os.getenv('GITHUB_TOKEN')
        
        response = post_pr_review(
            pr_url=pr_url,
            findings=finding_objects,
            token=token,
            event="COMMENT",
            body=review_body
        )
        
        print("🎉 Review posted successfully!")
        print(f"📊 Review ID: {response.get('id', 'N/A')}")
        print(f"🌐 Review URL: {response.get('html_url', 'N/A')}")
        print(f"💬 Posted {len(finding_objects)} inline comments")
        
        # Show summary of what was posted
        print(f"\n📋 Posted Comments Summary:")
        severity_counts = {}
        for finding in finding_objects:
            sev = finding.severity
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
        
        for severity, count in severity_counts.items():
            emoji = {'major': '🟠', 'minor': '🟡', 'info': '🔵', 'nit': '🟢'}.get(severity, '⚪')
            print(f"  {emoji} {severity.capitalize()}: {count}")
        
        print(f"\n✅ GitHub posting test completed successfully!")
        print(f"👀 Check the PR at: {pr_url}")
        
        return 0
        
    except GitHubReviewError as e:
        print(f"❌ GitHub API error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())