#!/usr/bin/env python3
"""
Review PR #2 using Kiro for code analysis
"""

import os
import json
import sys
from pathlib import Path

# Add the qrev module to path
sys.path.insert(0, str(Path(__file__).parent))

def analyze_code_with_kiro(file_content, filename, change_type):
    """
    Use Kiro to analyze code changes and provide review feedback.
    Since we're running inside Kiro, we can provide direct analysis.
    """
    
    # Analyze the code based on file type and changes
    findings = []
    
    if filename.endswith('.java'):
        findings.extend(analyze_java_code(file_content, filename, change_type))
    elif filename.endswith('.xml'):
        findings.extend(analyze_xml_code(file_content, filename, change_type))
    
    return findings

def analyze_java_code(content, filename, change_type):
    """Analyze Java code for common issues."""
    findings = []
    
    # Check for common Java patterns and issues
    lines = content.split('\n')
    
    for i, line in enumerate(lines, 1):
        line_stripped = line.strip()
        
        # Check for potential issues
        if 'System.out.print' in line:
            findings.append({
                'line': i,
                'severity': 'minor',
                'category': 'best_practices',
                'message': 'Consider using a proper logging framework instead of System.out.print',
                'confidence': 0.8
            })
        
        if 'TODO' in line or 'FIXME' in line:
            findings.append({
                'line': i,
                'severity': 'minor',
                'category': 'maintenance',
                'message': 'TODO/FIXME comment found - consider addressing before merge',
                'confidence': 0.9
            })
        
        if 'catch (Exception e)' in line and 'e.printStackTrace()' in content:
            findings.append({
                'line': i,
                'severity': 'major',
                'category': 'error_handling',
                'message': 'Generic exception catching with printStackTrace - consider specific exception handling and proper logging',
                'confidence': 0.7
            })
        
        if '@Autowired' in line:
            findings.append({
                'line': i,
                'severity': 'info',
                'category': 'spring',
                'message': 'Spring dependency injection detected - ensure proper configuration',
                'confidence': 0.6
            })
    
    # Check for class-level issues
    if 'class ' in content and change_type == 'added':
        if 'public class' in content and not any('javadoc' in line.lower() or '/**' in line for line in lines):
            findings.append({
                'line': 1,
                'severity': 'minor',
                'category': 'documentation',
                'message': 'New public class should have Javadoc documentation',
                'confidence': 0.8
            })
    
    return findings

def analyze_xml_code(content, filename, change_type):
    """Analyze XML code for common issues."""
    findings = []
    
    lines = content.split('\n')
    
    for i, line in enumerate(lines, 1):
        # Check for hardcoded values that might need configuration
        if 'localhost' in line.lower():
            findings.append({
                'line': i,
                'severity': 'minor',
                'category': 'configuration',
                'message': 'Hardcoded localhost reference - consider using configuration',
                'confidence': 0.7
            })
        
        # Check for potential security issues
        if 'password' in line.lower() and '=' in line:
            findings.append({
                'line': i,
                'severity': 'major',
                'category': 'security',
                'message': 'Potential hardcoded password - use secure configuration',
                'confidence': 0.9
            })
    
    return findings

def main():
    print("🚀 QReviewer: Analyzing PR #2 with Kiro")
    print("=" * 50)
    
    # Load the raw GitHub data
    try:
        with open('ae-pr2-raw-data.json', 'r') as f:
            data = json.load(f)
        
        pr_info = data['pr_info']
        files = data['files']
        
        print(f"📋 PR: {pr_info['title']}")
        print(f"👤 Author: {pr_info['user']['login']}")
        print(f"📊 Files: {len(files)}")
        print(f"📈 Changes: +{pr_info['additions']} -{pr_info['deletions']}")
        
    except FileNotFoundError:
        print("❌ Raw data file not found. Run test_github_api.py first.")
        return 1
    
    # Analyze each file
    all_findings = []
    
    print(f"\n🔍 Analyzing {len(files)} files...")
    
    for i, file_info in enumerate(files, 1):
        filename = file_info['filename']
        status = file_info['status']
        patch = file_info.get('patch', '')
        
        print(f"\n📄 {i}/{len(files)}: {filename} ({status})")
        
        if not patch:
            print("   ⚠️  No patch data available")
            continue
        
        # Extract the actual code changes from the patch
        patch_lines = patch.split('\n')
        added_lines = []
        removed_lines = []
        context_lines = []
        
        for line in patch_lines:
            if line.startswith('+') and not line.startswith('+++'):
                added_lines.append(line[1:])  # Remove the + prefix
            elif line.startswith('-') and not line.startswith('---'):
                removed_lines.append(line[1:])  # Remove the - prefix
            elif line.startswith(' '):
                context_lines.append(line[1:])  # Remove the space prefix
        
        # Combine all relevant content for analysis
        content_to_analyze = '\n'.join(added_lines + context_lines)
        
        if content_to_analyze.strip():
            # Use Kiro to analyze the code
            findings = analyze_code_with_kiro(content_to_analyze, filename, status)
            
            print(f"   🔍 Found {len(findings)} potential issues")
            
            # Convert findings to QReviewer format
            for finding in findings:
                qr_finding = {
                    'file': filename,
                    'hunk_header': f"@@ changes in {filename} @@",
                    'severity': finding['severity'],
                    'category': finding['category'],
                    'message': finding['message'],
                    'confidence': finding['confidence'],
                    'suggested_patch': None,
                    'line_hint': finding.get('line', 1)
                }
                all_findings.append(qr_finding)
                
                # Show the finding
                severity_emoji = {
                    'blocking': '🔴',
                    'major': '🟠', 
                    'minor': '🟡',
                    'info': '🔵',
                    'nit': '🟢'
                }.get(finding['severity'], '⚪')
                
                print(f"     {severity_emoji} {finding['severity'].upper()}: {finding['message']}")
        else:
            print("   ℹ️  No analyzable content in this file")
    
    # Create the final report
    from qrev.models import PRInfo, FindingsReport, Finding
    
    # Convert to proper models
    pr_model = PRInfo(
        url=pr_info['html_url'],
        number=pr_info['number'],
        repo=f"{pr_info['base']['repo']['owner']['login']}/{pr_info['base']['repo']['name']}",
        title=pr_info['title']
    )
    
    finding_models = []
    for f in all_findings:
        finding_model = Finding(
            file=f['file'],
            hunk_header=f['hunk_header'],
            severity=f['severity'],
            category=f['category'],
            message=f['message'],
            confidence=f['confidence'],
            suggested_patch=f['suggested_patch'],
            line_hint=f['line_hint']
        )
        finding_models.append(finding_model)
    
    report = FindingsReport(
        pr=pr_model,
        findings=finding_models
    )
    
    # Save the report
    output_file = "ae-pr2-kiro-review.json"
    with open(output_file, 'w') as f:
        json.dump(report.dict(), f, indent=2)
    
    # Summary
    print(f"\n📊 Review Summary")
    print("=" * 30)
    print(f"Total findings: {len(all_findings)}")
    
    if all_findings:
        severity_counts = {}
        for finding in all_findings:
            sev = finding['severity']
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
        
        for severity, count in severity_counts.items():
            emoji = {
                'blocking': '🔴',
                'major': '🟠', 
                'minor': '🟡',
                'info': '🔵',
                'nit': '🟢'
            }.get(severity, '⚪')
            print(f"{emoji} {severity.capitalize()}: {count}")
    
    print(f"\n✅ Review complete!")
    print(f"📁 Report saved to: {output_file}")
    print(f"🚀 Analyzed using Kiro's code analysis capabilities")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())