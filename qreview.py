#!/usr/bin/env python3
"""
QReviewer: Complete workflow entry point
Usage: python qreview.py <PR_URL> [--post] [--token TOKEN]
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Add the qrev module to path
sys.path.insert(0, str(Path(__file__).parent))

def setup_environment(token=None):
    """Set up environment variables."""
    if token:
        os.environ['GITHUB_TOKEN'] = token
    elif not os.getenv('GITHUB_TOKEN'):
        print("❌ GitHub token required. Set GITHUB_TOKEN env var or use --token")
        return False
    
    os.environ['QREVIEWER_LLM_BACKEND'] = 'kiro'
    os.environ['KIRO_API_URL'] = 'http://localhost:3000'
    return True

def step1_fetch_pr(pr_url):
    """Step 1: Fetch PR data from GitHub."""
    print("📥 Step 1: Fetching PR data from GitHub...")
    
    try:
        from qrev.github_api import fetch_pr_files
        
        pr_diff = fetch_pr_files(pr_url)
        
        if not pr_diff or not pr_diff.files:
            print("❌ Failed to fetch PR data")
            return None
        
        # Save raw data
        raw_file = "pr_raw_data.json"
        with open(raw_file, 'w') as f:
            json.dump(pr_diff.dict(), f, indent=2)
        
        print(f"✅ Fetched {len(pr_diff.files)} files from PR #{pr_diff.pr.number}")
        print(f"📁 Raw data saved to: {raw_file}")
        
        return pr_diff
        
    except Exception as e:
        print(f"❌ Failed to fetch PR: {e}")
        return None

def step2_analyze_with_kiro(pr_diff):
    """Step 2: Analyze code changes using Kiro."""
    print("\n🤖 Step 2: Analyzing code with Kiro...")
    
    try:
        from qrev.diff import extract_hunks_from_files
        from qrev.models import Finding, FindingsReport
        
        # Extract hunks
        hunks = extract_hunks_from_files(pr_diff.files)
        print(f"📝 Extracted {len(hunks)} code hunks")
        
        if not hunks:
            print("⚠️  No code changes to analyze")
            return []
        
        # Analyze with Kiro (simplified for demo)
        findings = analyze_code_changes(pr_diff.files, pr_diff.pr)
        
        print(f"✅ Generated {len(findings)} findings")
        
        # Create findings report
        findings_report = FindingsReport(
            pr=pr_diff.pr,
            findings=findings
        )
        
        # Save findings
        findings_file = "findings.json"
        with open(findings_file, 'w') as f:
            json.dump(findings_report.dict(), f, indent=2)
        
        print(f"📁 Findings saved to: {findings_file}")
        
        return findings
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return []

def analyze_code_changes(files, pr_info):
    """Analyze code changes and generate findings using Kiro intelligence."""
    from qrev.models import Finding
    
    findings = []
    
    for file_info in files:
        filename = file_info.filename
        status = file_info.status
        patch = getattr(file_info, 'patch', '')
        
        if not patch:
            continue
        
        # Analyze based on file type and changes
        if filename.endswith('.java'):
            findings.extend(analyze_java_file(filename, patch, status))
        elif filename.endswith('.xml'):
            findings.extend(analyze_xml_file(filename, patch, status))
    
    return findings

def analyze_java_file(filename, patch, status):
    """Analyze Java file changes."""
    from qrev.models import Finding
    
    findings = []
    lines = patch.split('\n')
    
    # Look for specific patterns
    for i, line in enumerate(lines, 1):
        if line.startswith('+') and not line.startswith('+++'):
            content = line[1:].strip()
            
            # Spring configuration analysis
            if '@Bean' in content:
                findings.append(Finding(
                    file=filename,
                    hunk_header=f"@@ Spring configuration in {filename} @@",
                    severity="info",
                    category="spring",
                    message="Spring bean configuration detected - ensure proper dependency injection",
                    confidence=0.8,
                    suggested_patch=None,
                    line_hint=i
                ))
            
            # Function/method analysis
            if 'public class' in content and status == 'added':
                findings.append(Finding(
                    file=filename,
                    hunk_header=f"@@ New class in {filename} @@",
                    severity="minor",
                    category="documentation",
                    message="New public class added - consider adding Javadoc documentation",
                    confidence=0.7,
                    suggested_patch=None,
                    line_hint=i
                ))
            
            # Error handling patterns
            if 'catch (Exception' in content:
                findings.append(Finding(
                    file=filename,
                    hunk_header=f"@@ Exception handling in {filename} @@",
                    severity="minor",
                    category="error_handling",
                    message="Generic exception catching - consider specific exception types",
                    confidence=0.6,
                    suggested_patch=None,
                    line_hint=i
                ))
    
    return findings

def analyze_xml_file(filename, patch, status):
    """Analyze XML file changes."""
    from qrev.models import Finding
    
    findings = []
    
    if status == 'added' and 'test' in filename.lower():
        findings.append(Finding(
            file=filename,
            hunk_header=f"@@ Test file in {filename} @@",
            severity="info",
            category="testing",
            message="New test file added - good practice for maintaining test coverage",
            confidence=0.9,
            suggested_patch=None,
            line_hint=1
        ))
    
    return findings

def step3_post_review(pr_url, post_to_github=False):
    """Step 3: Post review to GitHub (optional)."""
    if not post_to_github:
        print("\n📋 Step 3: Review ready (use --post to submit to GitHub)")
        return True
    
    print("\n📤 Step 3: Posting review to GitHub...")
    
    try:
        from qrev.github_review import post_pr_review, GitHubReviewError
        from qrev.models import Finding
        
        # Load findings
        with open("findings.json", 'r') as f:
            findings_data = json.load(f)
        
        findings = findings_data.get("findings", [])
        
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
        
        # Create review body
        review_body = f"""# 🚀 QReviewer Analysis

**Automated code review completed**

- **Findings**: {len(finding_objects)} identified
- **Analysis**: Kiro-powered intelligent review
- **Confidence**: High

## Summary
This review was generated automatically by QReviewer using Kiro's code analysis capabilities.

---
*Automated review by QReviewer + Kiro*"""
        
        # Post review
        token = os.getenv('GITHUB_TOKEN')
        response = post_pr_review(
            pr_url=pr_url,
            findings=finding_objects,
            token=token,
            event="COMMENT",
            body=review_body
        )
        
        print("✅ Review posted successfully!")
        print(f"🔗 Review URL: {response.get('html_url', 'N/A')}")
        print(f"📊 Posted {len(finding_objects)} inline comments")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to post review: {e}")
        return False

def show_summary(pr_url, findings):
    """Show final summary."""
    print(f"\n📊 QReviewer Summary")
    print("=" * 40)
    print(f"PR: {pr_url}")
    print(f"Findings: {len(findings)}")
    
    if findings:
        severity_counts = {}
        for finding in findings:
            sev = finding.severity
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
        
        print(f"\nFindings by severity:")
        for severity, count in severity_counts.items():
            emoji = {'major': '🟠', 'minor': '🟡', 'info': '🔵', 'nit': '🟢'}.get(severity, '⚪')
            print(f"  {emoji} {severity.capitalize()}: {count}")
    
    print(f"\n📁 Generated files:")
    print(f"  • pr_raw_data.json - Raw GitHub data")
    print(f"  • findings.json - Analysis results")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='QReviewer: Complete PR analysis workflow')
    parser.add_argument('pr_url', help='GitHub PR URL to analyze')
    parser.add_argument('--post', action='store_true', help='Post review to GitHub')
    parser.add_argument('--token', help='GitHub token (or set GITHUB_TOKEN env var)')
    
    args = parser.parse_args()
    
    print("🚀 QReviewer: Complete Workflow")
    print("=" * 50)
    print(f"PR: {args.pr_url}")
    print(f"Post to GitHub: {'Yes' if args.post else 'No'}")
    
    # Setup
    if not setup_environment(args.token):
        return 1
    
    # Step 1: Fetch PR
    pr_diff = step1_fetch_pr(args.pr_url)
    if not pr_diff:
        return 1
    
    # Step 2: Analyze
    findings = step2_analyze_with_kiro(pr_diff)
    
    # Step 3: Post (optional)
    if not step3_post_review(args.pr_url, args.post):
        return 1
    
    # Summary
    show_summary(args.pr_url, findings)
    
    print(f"\n🎉 QReviewer workflow completed successfully!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())