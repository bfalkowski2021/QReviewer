#!/usr/bin/env python3
"""
Quick test of the unified QReviewer workflow
"""

import os
import sys
from pathlib import Path

def main():
    """Test the workflow with our sample PR."""
    
    print("🧪 Testing QReviewer Unified Workflow")
    print("=" * 45)
    
    # Set environment
    os.environ['GITHUB_TOKEN'] = os.environ.get('GITHUB_TOKEN', 'your_github_token_here')
    
    # Test the workflow
    pr_url = "https://github.com/bfalkowski2021/ae/pull/2"
    
    print(f"Testing with PR: {pr_url}")
    print("Running: python qreview.py <PR_URL>")
    print()
    
    # Import and run the workflow
    sys.path.insert(0, str(Path(__file__).parent))
    
    try:
        # Simulate command line args
        sys.argv = ['qreview.py', pr_url]
        
        # Import and run
        import qreview
        result = qreview.main()
        
        if result == 0:
            print("\n🎉 Workflow test completed successfully!")
            
            # Check generated files
            if Path("pr_raw_data.json").exists():
                print("✅ pr_raw_data.json generated")
            if Path("findings.json").exists():
                print("✅ findings.json generated")
                
            print("\n📋 Next steps:")
            print("1. Review the generated files")
            print("2. Run with --post to submit to GitHub")
            print("3. Customize analysis for your needs")
            
        else:
            print("❌ Workflow test failed")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()