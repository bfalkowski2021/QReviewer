#!/bin/bash
# QReviewer Quick Install Script

echo "🚀 QReviewer Quick Install"
echo "=========================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found"
    echo "   Please install Python 3 first"
    exit 1
fi

# Check if pip3 is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not found"
    echo "   Please install pip3 first"
    exit 1
fi

echo "✅ Python 3 and pip3 found"

# Install core dependencies
echo "🔧 Installing core dependencies..."
pip3 install typer rich requests pydantic

if [ $? -eq 0 ]; then
    echo "✅ Core dependencies installed"
else
    echo "❌ Failed to install core dependencies"
    exit 1
fi

# Install optional dependencies (don't fail if these don't work)
echo "🔧 Installing optional dependencies..."
pip3 install fastapi uvicorn jinja2 httpx tenacity boto3 aiohttp 2>/dev/null || echo "⚠️  Some optional dependencies failed (this is usually OK)"

# Test the installation
echo "🧪 Testing installation..."
python3 -c "import typer, rich, requests, pydantic; print('✅ Core imports successful')" || {
    echo "❌ Installation test failed"
    exit 1
}

echo ""
echo "🎉 QReviewer is ready!"
echo ""
echo "📖 Next steps:"
echo "1. Set your GitHub token:"
echo "   export GITHUB_TOKEN='your_token_here'"
echo ""
echo "2. Test QReviewer:"
echo "   python3 qreview.py --help"
echo ""
echo "3. Run a review:"
echo "   python3 qreview.py https://github.com/owner/repo/pull/123"