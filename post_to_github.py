#!/usr/bin/env python3
"""
Use QReviewer CLI to post our Kiro analysis to GitHub PR #2
"""

import os
import subprocess
import sys
from pathlib import Path

def main():
    """Post the Kiro findings to GitHub using the CLI."""
    
    print("🚀 Posting Kiro Analysis to GitHub PR #2")
    print("=" * 50)
    
    # Set environment
    os.environ['GITHUB_TOKEN'] = os.environ.get('GITHUB_TOKEN', 'your_github_token_here')
    
    # Configuration
    pr_url = "https://github.com/bfalkowski2021/ae/pull/2"
    findings_file = "kiro_findings.json"
    
    # Check if findings file exists
    if not Path(findings_file).exists():
        print(f"❌ Findings file not found: {findings_file}")
        return 1
    
    # Create review body
    review_body = """🚀 QReviewer Analysis: Architectural Refactoring Review

This PR represents a high-quality architectural refactoring that significantly improves the codebase structure and maintainability.

Key Improvements:
✅ Single Responsibility Principle: Split monolithic function into focused components
✅ Spring Best Practices: Proper dependency injection and bean configuration  
✅ Service Layer Simplification: Removed complex conditional logic
✅ Test Coverage: Added integration tests for refactored functionality

Overall Assessment: High-quality architectural improvement with minor suggestions for enhancement.

Automated review by QReviewer with Kiro backend"""
    
    try:
        # Import and use the CLI function directly
        sys.path.insert(0, str(Path(__file__).parent))
        
        from qrev.github_review import post_pr_review, GitHubReviewError
        from qrev.models import Finding
        import json
        
        # Load findings
        print(f"📖 Loading findings from: {findings_file}")
        with open(findings_file, 'r') as f:
            findings_data = json.load(f)
        
        findings = findings_data.get("findings", [])
        print(f"✅ Found {len(findings)} findings to post")
        
        # Convert to Finding objects
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
        
        # Post review
        print(f"\n📝 Posting review to: {pr_url}")
        print(f"💬 Event type: COMMENT")
        print(f"🔍 Findings to post: {len(finding_objects)}")
        
        token = os.getenv('GITHUB_TOKEN')
        
        response = post_pr_review(
            pr_url=pr_url,
            findings=finding_objects,
            token=token,
            event="COMMENT",
            body=review_body
        )
        
        print("🎉 Review posted successfully!")
        print(f"🔗 Review ID: {response.get('id', 'N/A')}")
        print(f"🌐 Review URL: {response.get('html_url', 'N/A')}")
        print(f"📊 Posted {len(finding_objects)} inline comments")
        
        # Show summary
        print(f"\n📋 Posted Findings Summary:")
        severity_counts = {}
        for finding in finding_objects:
            sev = finding.severity
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
        
        for severity, count in severity_counts.items():
            emoji = {'major': '🟠', 'minor': '🟡', 'info': '🔵', 'nit': '🟢'}.get(severity, '⚪')
            print(f"  {emoji} {severity.capitalize()}: {count}")
        
        print(f"\n✅ QReviewer analysis successfully posted to GitHub!")
        print(f"👀 Check the PR for inline comments: {pr_url}")
        
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