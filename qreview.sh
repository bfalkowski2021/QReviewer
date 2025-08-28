#!/bin/bash
# QReviewer: Simple shell script wrapper
# Usage: ./qreview.sh <PR_URL> [--post]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
    echo -e "${BLUE}$1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check arguments
if [ $# -lt 1 ]; then
    echo "Usage: $0 <PR_URL> [--post]"
    echo "Example: $0 https://github.com/owner/repo/pull/123"
    echo "         $0 https://github.com/owner/repo/pull/123 --post"
    exit 1
fi

PR_URL="$1"
POST_FLAG="$2"

print_step "🚀 QReviewer: Complete Workflow"
echo "=================================================="
echo "PR: $PR_URL"
echo "Post to GitHub: $([ "$POST_FLAG" = "--post" ] && echo "Yes" || echo "No")"
echo ""

# Check if GitHub token is set
if [ -z "$GITHUB_TOKEN" ]; then
    print_error "GITHUB_TOKEN environment variable is required"
    echo "Set it with: export GITHUB_TOKEN='your_token_here'"
    exit 1
fi

# Check if Python script exists
if [ ! -f "qreview.py" ]; then
    print_error "qreview.py not found in current directory"
    exit 1
fi

# Run the Python workflow
print_step "Running QReviewer workflow..."

if [ "$POST_FLAG" = "--post" ]; then
    python qreview.py "$PR_URL" --post
else
    python qreview.py "$PR_URL"
fi

# Check if it succeeded
if [ $? -eq 0 ]; then
    print_success "QReviewer workflow completed successfully!"
    echo ""
    echo "📁 Generated files:"
    echo "  • pr_raw_data.json - Raw GitHub PR data"
    echo "  • findings.json - Analysis results"
    echo ""
    if [ "$POST_FLAG" != "--post" ]; then
        print_warning "Review not posted to GitHub. Use --post flag to submit."
        echo "To post: ./qreview.sh $PR_URL --post"
    fi
else
    print_error "QReviewer workflow failed"
    exit 1
fi