#!/usr/bin/env python3
"""Test script to review PR #2 from ae repository."""

import os
import sys
import json
from pathlib import Path

# Add the qrev module to the path
sys.path.insert(0, str(Path(__file__).parent))

# Set environment variables
os.environ['GITHUB_TOKEN'] = os.environ.get('GITHUB_TOKEN', 'your_github_token_here')
os.environ['QREVIEWER_LLM_BACKEND'] = 'amazon_q'
os.environ['Q_CLI_HOST'] = '192.168.1.100'
os.environ['Q_CLI_USER'] = 'bryan'
os.environ['Q_CLI_PORT'] = '22'

def main():
    try:
        from qrev.github_api import fetch_pr_files
        from qrev.diff import extract_hunks_from_files
        from qrev.llm_client import review_hunk, apply_security_heuristics
        from qrev.models import FindingsReport
        
        pr_url = "https://github.com/bfalkowski2021/ae/pull/2"
        
        print(f"🔍 Fetching PR: {pr_url}")
        
        # Fetch PR diff
        pr_diff = fetch_pr_files(pr_url)
        
        if not pr_diff or not pr_diff.files:
            print("❌ No files found in PR or failed to fetch")
            return 1
        
        print(f"📝 Found {len(pr_diff.files)} files in PR")
        
        # Extract hunks
        hunks = extract_hunks_from_files(pr_diff.files)
        print(f"🔍 Found {len(hunks)} hunks to review")
        
        if not hunks:
            print("⚠️  No hunks found to review")
            return 0
        
        # Review hunks
        all_findings = []
        
        print(f"🚀 Starting review of {len(hunks)} hunks...")
        
        for i, hunk in enumerate(hunks, 1):
            print(f"🔍 Processing hunk {i}/{len(hunks)}: {hunk.file_path} ({hunk.hunk_header})")
            
            try:
                findings = review_hunk(hunk, None)
                all_findings.extend(findings)
                print(f"✅ Completed hunk {i}/{len(hunks)}: {hunk.file_path} - Found {len(findings)} findings")
                if findings:
                    for finding in findings:
                        print(f"   📋 {finding.severity.upper()}: {finding.message}")
            except Exception as e:
                print(f"❌ Failed to review hunk {i}/{len(hunks)} in {hunk.file_path}: {e}")
        
        # Apply security heuristics
        print("🔒 Applying security heuristics...")
        all_findings = apply_security_heuristics(all_findings)
        
        # Create findings report
        findings_report = FindingsReport(
            pr=pr_diff.pr,
            findings=all_findings
        )
        
        # Write output
        output_file = "ae-pr2-review.json"
        with open(output_file, 'w') as f:
            json.dump(findings_report.dict(), f, indent=2)
        
        print(f"✅ Review complete! Found {len(all_findings)} issues")
        print(f"📁 Findings written to: {output_file}")
        
        # Show quick summary
        if all_findings:
            print("\n🔍 Quick Summary:")
            for finding in all_findings[:5]:  # Show first 5 findings
                severity_emoji = {"blocking": "🔴", "major": "🟠", "minor": "🟡", "nit": "🟢"}.get(finding.severity, "⚪")
                print(f"  {severity_emoji} {finding.severity.upper()}: {finding.message}")
                print(f"     📁 {finding.file} (line ~{finding.line_hint})")
            if len(all_findings) > 5:
                print(f"  ... and {len(all_findings) - 5} more findings")
        
        return 0
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())