# 🚀 QReviewer: All Entry Points

Complete list of ways to run the QReviewer workflow.

## 🎯 Main Entry Points

### 1. **Python Script** (Recommended)
```bash
# Basic usage
python qreview.py <PR_URL>

# With posting to GitHub
python qreview.py <PR_URL> --post

# With custom token
python qreview.py <PR_URL> --token your_token_here

# Example
python qreview.py https://github.com/bfalkowski2021/ae/pull/2
```

### 2. **Shell Script**
```bash
# Make executable (first time)
chmod +x qreview.sh

# Basic usage
./qreview.sh <PR_URL>

# With posting
./qreview.sh <PR_URL> --post

# Example
./qreview.sh https://github.com/bfalkowski2021/ae/pull/2
```

### 3. **Makefile Commands**
```bash
# Analyze only
make -f Makefile.qreview review PR=<PR_URL>

# Analyze and post
make -f Makefile.qreview post-review PR=<PR_URL>

# Test with sample PR
make -f Makefile.qreview test

# Example
make -f Makefile.qreview review PR=https://github.com/bfalkowski2021/ae/pull/2
```

## 🧪 Testing Entry Points

### Quick Test
```bash
# Test the workflow
python test_workflow.py

# Test individual components
python test_github_api.py
python kiro_pr2_analysis.py
```

### Sample PR Testing
```bash
# Our test PR (already analyzed)
export GITHUB_TOKEN="your_token"
python qreview.py https://github.com/bfalkowski2021/ae/pull/2
```

## 🔧 Advanced Usage

### Original CLI Commands
```bash
# Set environment
export GITHUB_TOKEN="your_token"
export QREVIEWER_LLM_BACKEND="kiro"

# Fetch and analyze (separate steps)
python -m qrev fetch --pr <PR_URL> --out pr-data.json
python -m qrev review --inp pr-data.json --out findings.json
python -m qrev post-review --pr <PR_URL> --findings findings.json

# All-in-one review (no posting)
python -m qrev review-only --pr <PR_URL> --out report.json

# Post existing findings
python -m qrev post-review --pr <PR_URL> --findings findings.json
```

### Direct Python Import
```python
# In your Python code
import sys
sys.path.append('/path/to/QReviewer')

from qrev.github_api import fetch_pr_files
from qrev.llm_client import review_hunk
from qrev.github_review import post_pr_review

# Use the functions directly
pr_diff = fetch_pr_files(pr_url)
# ... analyze and post
```

## 📁 File Structure

After running any workflow, you'll have:

```
QReviewer/
├── qreview.py              # Main unified script
├── qreview.sh              # Shell wrapper
├── Makefile.qreview        # Make commands
├── test_workflow.py        # Test script
├── pr_raw_data.json        # Generated: GitHub data
├── findings.json           # Generated: Analysis results
└── WORKFLOW_README.md      # Complete documentation
```

## 🎨 Examples for Different Scenarios

### 1. **Quick Analysis** (No GitHub posting)
```bash
python qreview.py https://github.com/owner/repo/pull/123
```

### 2. **Full Review with Posting**
```bash
python qreview.py https://github.com/owner/repo/pull/123 --post
```

### 3. **Batch Processing**
```bash
#!/bin/bash
for pr in 123 124 125; do
  python qreview.py "https://github.com/owner/repo/pull/$pr"
done
```

### 4. **CI/CD Integration**
```yaml
# GitHub Actions
- name: QReviewer Analysis
  run: python qreview.py ${{ github.event.pull_request.html_url }}
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### 5. **Custom Token**
```bash
python qreview.py <PR_URL> --token your_github_token_here
```

## 🚨 Environment Setup

### Required
```bash
export GITHUB_TOKEN="your_github_token_here"
```

### Optional
```bash
export QREVIEWER_LLM_BACKEND="kiro"          # Default: kiro
export KIRO_API_URL="http://localhost:3000"  # Default: localhost:3000
export QREVIEWER_VERBOSE="true"              # Enable debug logging
```

## 🎯 Choose Your Style

| Method | Best For | Pros | Cons |
|--------|----------|------|------|
| **Python Script** | Most users | Simple, flexible, cross-platform | Requires Python |
| **Shell Script** | Unix/Linux users | Native shell integration | Unix/Linux only |
| **Makefile** | Developers | Standard build tool, memorable commands | Requires make |
| **CLI Commands** | Advanced users | Fine-grained control, composable | More complex |
| **Direct Import** | Integration | Programmatic access | Requires Python knowledge |

## 🚀 Recommended Workflow

For most users, start with:

```bash
# 1. Set your token
export GITHUB_TOKEN="your_token_here"

# 2. Test with our sample PR
python qreview.py https://github.com/bfalkowski2021/ae/pull/2

# 3. Use with your own PRs
python qreview.py https://github.com/your-org/your-repo/pull/123

# 4. When ready, post to GitHub
python qreview.py https://github.com/your-org/your-repo/pull/123 --post
```

---

**All entry points are ready to use!** 🎉  
Pick the one that fits your workflow best.