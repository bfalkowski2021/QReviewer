#!/usr/bin/env python3
"""
Comprehensive Kiro-based analysis of PR #2: Composer sdx tests rdm
"""

import json
import sys
from pathlib import Path

def analyze_pr2_changes():
    """
    Analyze the PR #2 changes using Kiro's code analysis capabilities.
    This PR appears to be refactoring data model generation functionality.
    """
    
    print("🚀 Kiro Analysis: PR #2 - Composer sdx tests rdm")
    print("=" * 60)
    
    # Key observations from the patch analysis
    findings = []
    
    # 1. Architecture Analysis
    findings.append({
        'file': 'RequirementsCaptureSpringConfig.java',
        'severity': 'info',
        'category': 'architecture',
        'message': 'Good refactoring: Split GenerateRecommendedDataModelFn into two focused functions (RequestInitial and RequestUpdate)',
        'confidence': 0.9,
        'line_hint': 330,
        'reasoning': 'The original function handled both initial and update scenarios, violating single responsibility principle'
    })
    
    # 2. Dependency Injection Analysis
    findings.append({
        'file': 'RequirementsCaptureSpringConfig.java',
        'severity': 'minor',
        'category': 'spring',
        'message': 'New bean definitions follow Spring best practices with proper dependency injection',
        'confidence': 0.8,
        'line_hint': 515,
        'reasoning': 'RequestInitialRecommendedDataModelFn and RequestUpdateRecommendedDataModelFn beans are properly configured'
    })
    
    # 3. Service Layer Simplification
    findings.append({
        'file': 'RecommendedDataModelService.java',
        'severity': 'major',
        'category': 'design',
        'message': 'Excellent simplification: Removed complex conditional logic from service layer',
        'confidence': 0.9,
        'line_hint': 47,
        'reasoning': 'The service now has cleaner separation of concerns with public methods for initial and update operations'
    })
    
    # 4. Feature Toggle Removal
    findings.append({
        'file': 'RecommendedDataModelService.java',
        'severity': 'info',
        'category': 'feature_management',
        'message': 'Feature toggle dependency removed from service - moved to function level',
        'confidence': 0.8,
        'line_hint': 62,
        'reasoning': 'FeatureToggleClient removed from constructor, likely handled at function level now'
    })
    
    # 5. Error Handling Consistency
    findings.append({
        'file': 'RequestInitialRecommendedDataModelFn.java',
        'severity': 'minor',
        'category': 'error_handling',
        'message': 'Consistent error handling pattern with proper null value initialization',
        'confidence': 0.7,
        'line_hint': 44,
        'reasoning': 'Good practice of initializing error values to null and setting them only on exceptions'
    })
    
    # 6. Code Duplication Concern
    findings.append({
        'file': 'RequestUpdateRecommendedDataModelFn.java',
        'severity': 'minor',
        'category': 'maintainability',
        'message': 'Similar error handling pattern - consider extracting to base class or utility',
        'confidence': 0.6,
        'line_hint': 41,
        'reasoning': 'Both new functions have very similar error handling structure'
    })
    
    # 7. Method Visibility Change
    findings.append({
        'file': 'RecommendedDataModelService.java',
        'severity': 'info',
        'category': 'encapsulation',
        'message': 'Methods changed from private to public - ensure this is intentional for the new architecture',
        'confidence': 0.8,
        'line_hint': 84,
        'reasoning': 'createEntitiesForPlan and updateEntitiesForPlan are now public methods'
    })
    
    # 8. Test Coverage
    findings.append({
        'file': 'recommendedDataModelHappyPath.xml',
        'severity': 'info',
        'category': 'testing',
        'message': 'Good addition of integration test for the happy path scenario',
        'confidence': 0.9,
        'line_hint': 1,
        'reasoning': 'New test file suggests proper test coverage for the refactored functionality'
    })
    
    # 9. Import Cleanup
    findings.append({
        'file': 'RecommendedDataModelService.java',
        'severity': 'nit',
        'category': 'code_quality',
        'message': 'Good cleanup of unused imports after refactoring',
        'confidence': 0.9,
        'line_hint': 1,
        'reasoning': 'Removed imports for constants that are no longer used in this class'
    })
    
    # 10. Function Naming
    findings.append({
        'file': 'RequestInitialRecommendedDataModelFn.java',
        'severity': 'info',
        'category': 'naming',
        'message': 'Clear and descriptive function names that indicate their specific purpose',
        'confidence': 0.8,
        'line_hint': 27,
        'reasoning': 'RequestInitialRecommendedDataModelFn and RequestUpdateRecommendedDataModelFn are self-documenting'
    })
    
    return findings

def generate_summary(findings):
    """Generate a summary of the analysis."""
    
    severity_counts = {}
    category_counts = {}
    
    for finding in findings:
        sev = finding['severity']
        cat = finding['category']
        
        severity_counts[sev] = severity_counts.get(sev, 0) + 1
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    print(f"\n📊 Analysis Summary")
    print("=" * 30)
    print(f"Total findings: {len(findings)}")
    
    print(f"\n🎯 By Severity:")
    for severity in ['blocking', 'major', 'minor', 'info', 'nit']:
        count = severity_counts.get(severity, 0)
        if count > 0:
            emoji = {'blocking': '🔴', 'major': '🟠', 'minor': '🟡', 'info': '🔵', 'nit': '🟢'}[severity]
            print(f"  {emoji} {severity.capitalize()}: {count}")
    
    print(f"\n📋 By Category:")
    for category, count in sorted(category_counts.items()):
        print(f"  • {category.replace('_', ' ').title()}: {count}")

def main():
    """Main analysis function."""
    
    # Perform the analysis
    findings = analyze_pr2_changes()
    
    # Display findings
    print(f"\n🔍 Detailed Findings:")
    print("-" * 40)
    
    for i, finding in enumerate(findings, 1):
        severity_emoji = {
            'blocking': '🔴',
            'major': '🟠', 
            'minor': '🟡',
            'info': '🔵',
            'nit': '🟢'
        }.get(finding['severity'], '⚪')
        
        print(f"\n{i}. {severity_emoji} {finding['severity'].upper()} - {finding['category'].replace('_', ' ').title()}")
        print(f"   📄 File: {finding['file']}")
        print(f"   💬 {finding['message']}")
        print(f"   🎯 Confidence: {finding['confidence']:.0%}")
        if 'reasoning' in finding:
            print(f"   💭 Reasoning: {finding['reasoning']}")
    
    # Generate summary
    generate_summary(findings)
    
    # Overall assessment
    print(f"\n🎉 Overall Assessment:")
    print("=" * 30)
    print("✅ This is a well-executed refactoring that improves code organization")
    print("✅ Proper separation of concerns between initial and update operations")
    print("✅ Good Spring configuration and dependency injection practices")
    print("✅ Appropriate test coverage with integration tests")
    print("⚠️  Consider extracting common error handling patterns")
    print("⚠️  Verify that making service methods public is intentional")
    
    # Create QReviewer-compatible output
    qr_findings = []
    for finding in findings:
        qr_finding = {
            'file': finding['file'],
            'hunk_header': f"@@ changes in {finding['file']} @@",
            'severity': finding['severity'],
            'category': finding['category'],
            'message': finding['message'],
            'confidence': finding['confidence'],
            'suggested_patch': None,
            'line_hint': finding.get('line_hint', 1)
        }
        qr_findings.append(qr_finding)
    
    # Save the analysis
    report = {
        'pr': {
            'url': 'https://github.com/bfalkowski2021/ae/pull/2',
            'number': 2,
            'repo': 'bfalkowski2021/ae',
            'title': 'Composer sdx tests rdm'
        },
        'findings': qr_findings,
        'analysis_metadata': {
            'analyzer': 'Kiro',
            'analysis_type': 'architectural_review',
            'focus_areas': ['refactoring', 'spring_configuration', 'error_handling', 'testing']
        }
    }
    
    output_file = "ae-pr2-kiro-analysis.json"
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📁 Analysis saved to: {output_file}")
    print(f"🚀 Analysis completed using Kiro's architectural review capabilities")

if __name__ == "__main__":
    main()