#!/usr/bin/env python3
"""
Test QReviewer on PR #2 from bfalkowski2021/ae using Kiro backend
"""

import os
import json
import sys
from pathlib import Path

# Add the qrev module to path
sys.path.insert(0, str(Path(__file__).parent))

from qrev.github_api import fetch_pr_files
from qrev.diff import extract_hunks_from_files
from qrev.llm_client import review_hunk
from qrev.models import FindingsReport

def main():
    # Set up environment
    os.environ['GITHUB_TOKEN'] = os.environ.get('GITHUB_TOKEN', 'your_github_token_here')
    os.environ['QREVIEWER_LLM_BACKEND'] = 'kiro'
    
    pr_url = "https://github.com/bfalkowski2021/ae/pull/2"
    
    print(f"🔍 Testing QReviewer on: {pr_url}")
    print(f"🤖 Using Kiro backend")
    
    try:
        # Step 1: Fetch PR files
        print("\n📥 Fetching PR files...")
        pr_diff = fetch_pr_files(pr_url)
        print(f"✅ Fetched {len(pr_diff.files)} files from PR #{pr_diff.pr.number}")
        
        # Step 2: Extract hunks
        print("\n📝 Extracting hunks...")
        hunks = extract_hunks_from_files(pr_diff.files)
        print(f"✅ Found {len(hunks)} hunks to review")
        
        if not hunks:
            print("⚠️  No hunks found to review")
            return
        
        # Step 3: Review first few hunks as test
        print(f"\n🚀 Testing review on first 3 hunks...")
        all_findings = []
        
        for i, hunk in enumerate(hunks[:3], 1):
            print(f"\n🔍 Processing hunk {i}: {hunk.file_path}")
            print(f"   Header: {hunk.hunk_header}")
            
            try:
                findings = review_hunk(hunk, None)
                all_findings.extend(findings)
                print(f"✅ Found {len(findings)} findings")
                
                for finding in findings:
                    print(f"   📋 {finding.severity.upper()}: {finding.message}")
                    
            except Exception as e:
                print(f"❌ Failed to review hunk: {e}")
        
        # Step 4: Save results
        findings_report = FindingsReport(
            pr=pr_diff.pr,
            findings=all_findings
        )
        
        output_file = "ae-pr2-kiro-test.json"
        with open(output_file, 'w') as f:
            json.dump(findings_report.dict(), f, indent=2)
        
        print(f"\n✅ Test complete!")
        print(f"📁 Results saved to: {output_file}")
        print(f"🔍 Total findings: {len(all_findings)}")
        
        # Show summary
        if all_findings:
            severity_counts = {}
            for finding in all_findings:
                severity_counts[finding.severity] = severity_counts.get(finding.severity, 0) + 1
            
            print("\n📊 Findings summary:")
            for severity, count in severity_counts.items():
                print(f"   {severity}: {count}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()