# 🚀 QReviewer: Complete Workflow Guide

Simple, unified entry points to run the complete QReviewer workflow with Kiro backend.

## 🎯 Quick Start

### Option 1: Python Script (Recommended)
```bash
# Set your GitHub token
export GITHUB_TOKEN="your_github_token_here"

# Analyze a PR (no posting)
python qreview.py https://github.com/owner/repo/pull/123

# Analyze and post to GitHub
python qreview.py https://github.com/owner/repo/pull/123 --post
```

### Option 2: Shell Script
```bash
# Set your GitHub token
export GITHUB_TOKEN="your_github_token_here"

# Analyze a PR
./qreview.sh https://github.com/owner/repo/pull/123

# Analyze and post to GitHub
./qreview.sh https://github.com/owner/repo/pull/123 --post
```

### Option 3: Makefile Commands
```bash
# Set your GitHub token
export GITHUB_TOKEN="your_github_token_here"

# Analyze a PR
make -f Makefile.qreview review PR=https://github.com/owner/repo/pull/123

# Analyze and post to GitHub
make -f Makefile.qreview post-review PR=https://github.com/owner/repo/pull/123

# Test with sample PR
make -f Makefile.qreview test
```

## 📋 What It Does

The workflow performs these steps automatically:

### Step 1: 📥 Fetch PR Data
- Connects to GitHub API using your token
- Downloads complete PR information
- Extracts file changes and patch data
- Saves raw data to `pr_raw_data.json`

### Step 2: 🤖 Analyze with Kiro
- Processes code changes using Kiro intelligence
- Identifies patterns, issues, and improvements
- Generates findings with confidence ratings
- Saves analysis to `findings.json`

### Step 3: 📤 Post Review (Optional)
- Formats findings as GitHub review comments
- Posts inline comments on specific code lines
- Adds overall review summary
- Links back to QReviewer for transparency

## 🔧 Setup

### Prerequisites
```bash
# 1. Python 3.7+
python --version

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set GitHub token
export GITHUB_TOKEN="your_github_token_here"
```

### GitHub Token Setup
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate new token with these permissions:
   - `repo` (for private repos) or `public_repo` (for public repos)
   - `pull_requests` (to read and comment on PRs)
3. Set the token: `export GITHUB_TOKEN="your_token"`

## 📊 Output Files

After running, you'll get:

### `pr_raw_data.json`
Complete GitHub PR data including:
- PR metadata (title, author, status)
- File changes with patch information
- Commit details and timestamps

### `findings.json`
QReviewer analysis results:
- Individual findings with severity levels
- Confidence ratings for each finding
- Suggested improvements and patches
- File locations and line numbers

## 🎨 Example Usage

### Analyze Our Test PR
```bash
# The PR we've been testing
export GITHUB_TOKEN="your_token"
python qreview.py https://github.com/bfalkowski2021/ae/pull/2
```

### Expected Output
```
🚀 QReviewer: Complete Workflow
==================================================
PR: https://github.com/bfalkowski2021/ae/pull/2
Post to GitHub: No

📥 Step 1: Fetching PR data from GitHub...
✅ Fetched 11 files from PR #2
📁 Raw data saved to: pr_raw_data.json

🤖 Step 2: Analyzing code with Kiro...
📝 Extracted 15 code hunks
✅ Generated 7 findings
📁 Findings saved to: findings.json

📋 Step 3: Review ready (use --post to submit to GitHub)

📊 QReviewer Summary
========================================
PR: https://github.com/bfalkowski2021/ae/pull/2
Findings: 7

Findings by severity:
  🟠 Major: 1
  🟡 Minor: 3
  🔵 Info: 3

📁 Generated files:
  • pr_raw_data.json - Raw GitHub data
  • findings.json - Analysis results

🎉 QReviewer workflow completed successfully!
```

## 🔍 Analysis Types

QReviewer with Kiro analyzes:

### Java Files
- **Spring Configuration**: Bean definitions, dependency injection
- **Architecture Patterns**: Design principles, code organization
- **Error Handling**: Exception patterns, logging practices
- **Code Quality**: Documentation, naming conventions

### XML Files
- **Configuration**: Spring XML, test configurations
- **Test Coverage**: New test files and test patterns
- **Security**: Hardcoded values, configuration issues

### General
- **File Changes**: Additions, deletions, modifications
- **Architectural Impact**: Design pattern compliance
- **Best Practices**: Industry standards and conventions

## 🎛️ Command Options

### Python Script Options
```bash
python qreview.py <PR_URL> [OPTIONS]

Options:
  --post          Post review to GitHub (default: analyze only)
  --token TOKEN   GitHub token (or set GITHUB_TOKEN env var)
  -h, --help      Show help message
```

### Makefile Targets
```bash
make -f Makefile.qreview <target>

Targets:
  help           Show available commands
  review         Analyze PR without posting
  post-review    Analyze and post to GitHub
  test           Test with sample PR
  clean          Remove generated files
  check-env      Verify environment setup
  status         Show status of generated files
```

## 🚨 Troubleshooting

### Common Issues

**"GitHub token required"**
```bash
export GITHUB_TOKEN="your_token_here"
```

**"Failed to fetch PR"**
- Check PR URL format: `https://github.com/owner/repo/pull/number`
- Verify token has correct permissions
- Ensure PR exists and is accessible

**"No findings generated"**
- PR might have no code changes
- Only text/documentation changes
- Check `pr_raw_data.json` for actual changes

**"Failed to post review"**
- Token needs `pull_requests` permission
- Can't post to closed/merged PRs
- Rate limiting (wait and retry)

### Debug Mode
```bash
# Add verbose logging
QREVIEWER_VERBOSE=true python qreview.py <PR_URL>
```

## 🔄 Integration

### GitHub Actions
```yaml
name: QReviewer
on: [pull_request]
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Run QReviewer
      run: python qreview.py ${{ github.event.pull_request.html_url }} --post
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### CI/CD Pipeline
```bash
# In your CI script
if [ "$CI_EVENT" = "pull_request" ]; then
  python qreview.py "$PR_URL" --post
fi
```

## 📈 Next Steps

1. **Customize Analysis**: Modify `analyze_java_file()` for your coding standards
2. **Add Languages**: Extend analysis for Python, JavaScript, etc.
3. **Custom Rules**: Add project-specific guidelines
4. **Integration**: Set up automated PR reviews
5. **Reporting**: Add metrics and trend analysis

---

**Ready to use!** 🎉  
Start with: `python qreview.py <YOUR_PR_URL>`